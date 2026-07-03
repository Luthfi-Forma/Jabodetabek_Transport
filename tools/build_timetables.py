"""Bangkitkan jadwal perjalanan (timetable) dari parameter headway.

Input : public/data/lines.json          (stasiun + distAlong per jalur)
        data/curated/service_params.json (headway, jam operasi, kecepatan)
Output: public/data/timetables/<LINE>_<weekday|weekend>.json

Skema trip sama persis dengan yang nanti dipakai data KRL asli (fase 5):
{ "id": ..., "dest": kode stasiun tujuan, "stops": [{"s": kode, "a": detik, "d": detik}] }
Waktu = detik sejak tengah malam WIB.
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "public" / "data" / "timetables"


def hm_to_sec(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 3600 + int(m) * 60


def departures(svc: dict):
    """Daftar waktu keberangkatan dari stasiun awal menurut pita headway."""
    t = hm_to_sec(svc["first"])
    last = hm_to_sec(svc["last"])
    bands = [
        (hm_to_sec(b["from"]), hm_to_sec(b["to"]), b["sec"])
        for b in svc["headways"]
    ]
    out = []
    while t <= last:
        out.append(t)
        sec = next((s for f, to, s in bands if f <= t < to), bands[-1][2])
        t += sec
    return out


def make_trips(line, params, service_name):
    svc = params.get(service_name) or params["weekday"]
    speed_ms = params["avgSpeedKmh"] / 3.6
    dwell = params["dwellSec"]
    stations = line["stations"]

    trips = []
    for direction, order in (("1", stations), ("2", list(reversed(stations)))):
        for i, t0 in enumerate(departures(svc)):
            stops = []
            t = t0
            for j, st in enumerate(order):
                if j == 0:
                    stops.append({"s": st["code"], "a": t, "d": t})
                else:
                    seg_m = abs(st["distAlong"] - order[j - 1]["distAlong"]) * 1000
                    t += round(seg_m / speed_ms)
                    arr = t
                    dep = arr if j == len(order) - 1 else arr + dwell
                    stops.append({"s": st["code"], "a": arr, "d": dep})
                    t = dep
            svc_tag = "wd" if service_name == "weekday" else "we"
            trips.append({
                "id": f"{line['id']}-{svc_tag}-{direction}-{i:03d}",
                "dest": order[-1]["code"],
                "stops": stops,
            })
    return trips


def main():
    lines = json.loads(
        (ROOT / "public" / "data" / "lines.json").read_text(encoding="utf-8")
    )["lines"]
    params_all = json.loads(
        (ROOT / "data" / "curated" / "service_params.json").read_text(encoding="utf-8")
    )["lines"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    problems = 0
    for line in lines:
        params = params_all.get(line["id"])
        if not params:
            print(f"{line['id']}: tidak ada service_params, lewati")
            problems += 1
            continue
        for service in ("weekday", "weekend"):
            trips = make_trips(line, params, service)
            # validasi: waktu tiap trip harus naik terus
            for tr in trips:
                seq = [x for st in tr["stops"] for x in (st["a"], st["d"])]
                if seq != sorted(seq):
                    print(f"  !! {tr['id']}: waktu tidak monoton")
                    problems += 1
            out = {"lineId": line["id"], "service": service,
                   "generated": True, "trips": trips}
            path = OUT_DIR / f"{line['id']}_{service}.json"
            path.write_text(json.dumps(out), encoding="utf-8")
            dur = trips[0]["stops"][-1]["a"] - trips[0]["stops"][0]["d"]
            print(f"{line['id']} {service}: {len(trips)} trip, "
                  f"durasi sekali jalan {dur // 60} menit")

    print(f"\nselesai, {problems} masalah")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
