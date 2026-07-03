"""Ambil jadwal KRL ASLI dari comuline API dan tulis ke skema timetable kita.

Sumber : https://api.comuline.com (proyek open-source comuline/api,
         menyalin jadwal resmi KAI Commuter setiap tengah malam)
Output : public/data/timetables/<B|C|R|T|TP>_weekday.json
         (menimpa file hasil generator headway; file weekend tetap
         hasil generator sebagai cadangan)

Cara kerja:
1. Petakan stasiun kurasi kita -> ID stasiun comuline (via nama).
2. Unduh jadwal keberangkatan per stasiun (cache di data/raw/comuline/).
3. Kelompokkan per train_id -> urutan berhenti satu perjalanan (trip).
4. Tulis dengan skema yang sama persis dengan generator.

Catatan: API dijalankan pihak ketiga; kalau mati, jalankan lagi
build_timetables.py untuk kembali ke jadwal perkiraan.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "comuline"
OUT_DIR = ROOT / "public" / "data" / "timetables"
BASE = "https://api.comuline.com"

KRL_LINES = ["B", "C", "R", "T", "TP"]

# nama kurasi -> nama comuline yang tidak cocok otomatis
ALIASES = {
    "universitaspancasila": ["univpancasila", "universitaspancasila"],
    "universitasindonesia": ["univindonesia", "universitasindonesia"],
    "tanjungpriok": ["tanjungpriuk", "tanjungpriok"],
}

DWELL_SEC = 25  # jeda berhenti yang ditampilkan (data asli hanya punya jam berangkat)


def curl_json(url):
    # python urllib ditolak TLS server ini; pakai curl bawaan Windows
    r = subprocess.run(
        ["curl.exe", "-sL", "-m", "60", url],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"curl gagal untuk {url}: rc={r.returncode}")
    return json.loads(r.stdout)


def norm(name):
    return "".join(ch for ch in name.lower() if ch.isalnum())


def hms_to_sec(ts):
    # "2024-11-12 17:01:00.964+00" -> detik sejak tengah malam WIB.
    # comuline menyimpan jam dalam UTC (WIB - 7 jam), jadi digeser +7 jam.
    hms = ts.split(" ")[1].split(".")[0]
    h, m, s = (int(x) for x in hms.split(":"))
    return (h * 3600 + m * 60 + s + 7 * 3600) % 86400


def classify(line_str, route_str):
    """Nama line comuline -> ID jalur kita (None = bukan jalur yang dipakai)."""
    ls = norm(line_str)
    rs = norm(route_str)
    if "bogor" in ls:
        return "B"
    if "cikarang" in ls:
        # pola via Pasar Senen lewat stasiun yang tak ada di geometri kita
        if "pasarsenen" in rs:
            return None
        return "C"
    if "rangkasbitung" in ls or "parungpanjang" in ls or "tigaraksa" in ls:
        return "R"
    if "tangerang" in ls:
        return "T"
    if "priuk" in ls or "priok" in ls:
        return "TP"
    return None


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    meta_all = json.loads(
        (ROOT / "data" / "curated" / "lines_meta.json").read_text(encoding="utf-8")
    )
    lines = {l["id"]: l for l in meta_all["lines"] if l["id"] in KRL_LINES}

    # 1) daftar stasiun comuline
    st_cache = RAW_DIR / "stations.json"
    if st_cache.exists():
        stations = json.loads(st_cache.read_text(encoding="utf-8"))
    else:
        stations = curl_json(f"{BASE}/v1/station")["data"]
        st_cache.write_text(json.dumps(stations), encoding="utf-8")
    api_by_norm = {norm(s["name"]): s["id"] for s in stations if s["type"] == "KRL"}

    def find_api_id(name):
        n = norm(name)
        if n in api_by_norm:
            return api_by_norm[n]
        for alias in ALIASES.get(n, []):
            if alias in api_by_norm:
                return api_by_norm[alias]
        cands = [k for k in api_by_norm if k.startswith(n) or n.startswith(k)]
        if len(cands) == 1:
            return api_by_norm[cands[0]]
        return None

    # 2) pemetaan stasiun per jalur + kumpulan stasiun unik
    rev = {}      # lineId -> {api_id: kode}
    api_ids = set()
    missing = []
    for line_id, meta in lines.items():
        rev[line_id] = {}
        for st in meta["stations"]:
            api_id = find_api_id(st["name"])
            if api_id is None:
                missing.append(f"{line_id}: {st['name']}")
                continue
            rev[line_id][api_id] = st["code"]
            api_ids.add(api_id)
    if missing:
        # tak fatal: stasiun yang hilang cuma dilewati tanpa jadwal berhenti
        # (mis. Jatake, stasiun baru yang belum ada di data comuline)
        print(f"  peringatan, stasiun tanpa data comuline: {missing}")
        if len(missing) > 5:
            print("!! terlalu banyak yang hilang, cek pemetaan nama")
            sys.exit(1)

    # 3) unduh jadwal per stasiun (cache)
    schedules = {}
    for i, api_id in enumerate(sorted(api_ids)):
        cache = RAW_DIR / f"sched_{api_id}.json"
        if cache.exists():
            schedules[api_id] = json.loads(cache.read_text(encoding="utf-8"))
        else:
            print(f"  unduh {api_id} ({i + 1}/{len(api_ids)}) ...")
            data = curl_json(f"{BASE}/v1/schedule/{api_id}")["data"]
            schedules[api_id] = data
            cache.write_text(json.dumps(data), encoding="utf-8")
            time.sleep(0.4)

    # 4) kelompokkan per jalur -> per (train_id, route).
    # Nomor kereta bisa dipakai ulang saat jadwal berubah (data comuline
    # berisi campuran snapshot beda tanggal), jadi route ikut jadi kunci;
    # varian usang yang tercampur akan gugur di uji waktu-monoton di bawah.
    per_line = {lid: {} for lid in KRL_LINES}
    for api_id, entries in schedules.items():
        for e in entries:
            line_id = classify(e.get("line", ""), e.get("route", ""))
            if line_id is None or api_id not in rev[line_id]:
                continue
            code = rev[line_id][api_id]
            key = (e["train_id"], e.get("route", ""))
            tr = per_line[line_id].setdefault(key, {"stops": {}, "date": ""})
            tr["stops"][code] = hms_to_sec(e["departs_at"])
            tr["dest_api"] = e["station_destination_id"]
            tr["arr"] = hms_to_sec(e["arrives_at"])
            tr["date"] = max(tr["date"], e["departs_at"][:10])

    # nomor kereta dengan >1 varian route: pakai snapshot terbaru saja
    for line_id, trains in per_line.items():
        newest = {}
        for (train_id, route), info in trains.items():
            cur = newest.get(train_id)
            if cur is None or info["date"] > cur[1]:
                newest[train_id] = (route, info["date"])
        per_line[line_id] = {
            k: v for k, v in trains.items() if newest[k[0]][0] == k[1]
        }

    # jarak-sepanjang-jalur per kode stasiun (untuk mengurutkan arah trip)
    lines_pub = json.loads(
        (ROOT / "public" / "data" / "lines.json").read_text(encoding="utf-8")
    )["lines"]
    km_by_code = {
        s["code"]: s["distAlong"]
        for l in lines_pub for s in l["stations"]
    }

    # 5) susun trip
    counts = {}
    for line_id, trains in per_line.items():
        trips, dropped = [], 0
        used_ids = set()
        for (train_id, _route), info in sorted(trains.items()):
            dest_code = rev[line_id].get(info["dest_api"])
            if dest_code is None or len(info["stops"]) < 2:
                dropped += 1
                continue

            # urutkan menurut POSISI di jalur, bergerak menuju stasiun tujuan
            # (mengurutkan berdasarkan jam kacau saat trip melewati tengah malam)
            items = list(info["stops"].items())
            km_first = min(km_by_code[c] for c, _ in items)
            km_last = max(km_by_code[c] for c, _ in items)
            dest_km = km_by_code[dest_code]
            ascending = abs(dest_km - km_last) <= abs(dest_km - km_first)
            items.sort(key=lambda kv: km_by_code[kv[0]], reverse=not ascending)

            # jam boleh melewati tengah malam sekali; selain itu data rusak
            seq, prev, offset, bad = [], None, 0, False
            for code, t in items:
                t += offset
                if prev is not None and t < prev:
                    if prev - t > 43200:
                        offset += 86400
                        t += 86400
                    else:
                        bad = True
                        break
                seq.append((code, t))
                prev = t
            if bad:
                dropped += 1
                continue

            # stasiun akhir: pakai waktu tiba di tujuan
            arr = info["arr"]
            while arr < seq[-1][1]:
                arr += 86400
            if seq[-1][0] != dest_code:
                seq.append((dest_code, arr))

            # tolak durasi tak masuk akal (data korup)
            if seq[-1][1] - seq[0][1] > 4 * 3600:
                dropped += 1
                continue

            stops = []
            for j, (code, t) in enumerate(seq):
                if j == 0:
                    stops.append({"s": code, "a": t, "d": t})
                else:
                    a = max(stops[-1]["d"] + 10, t - DWELL_SEC)
                    d = t if j < len(seq) - 1 else a
                    stops.append({"s": code, "a": a, "d": max(a, d)})
            flat = [x for st in stops for x in (st["a"], st["d"])]
            if flat != sorted(flat):
                dropped += 1
                continue
            trip_id = f"{line_id}-krl-{train_id}"
            while trip_id in used_ids:
                trip_id += "x"
            used_ids.add(trip_id)
            trips.append({"id": trip_id, "dest": dest_code, "stops": stops})

        trips.sort(key=lambda tr: tr["stops"][0]["d"])
        counts[line_id] = (len(trips), dropped)
        out = {"lineId": line_id, "service": "weekday",
               "generated": False, "source": "comuline", "trips": trips}
        (OUT_DIR / f"{line_id}_weekday.json").write_text(
            json.dumps(out), encoding="utf-8")

    print("\nhasil (trip valid, dibuang):")
    for lid, (n, d) in counts.items():
        first = "-"
        path = OUT_DIR / f"{lid}_weekday.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["trips"]:
            t0 = data["trips"][0]["stops"][0]["d"]
            first = f"{t0 // 3600:02d}:{t0 % 3600 // 60:02d}"
        print(f"  {lid}: {n} trip (buang {d}), kereta pertama {first}")


if __name__ == "__main__":
    main()
