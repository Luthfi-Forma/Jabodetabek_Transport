"""Tambahkan 14 koridor BRT TransJakarta dari GTFS resmi ke data aplikasi.

Input : data/raw/gtfs/extracted/  (unzip dari gtfs.transjakarta.co.id)
Output: menambah/menimpa entri mode "brt" (lineId TJ1..TJ14) di
        public/data/lines.geojson, stations.geojson, lines.json,
        dan menulis timetables/TJ<n>_{weekday|weekend}.json

Pendekatan V1 per koridor:
- Geometri & urutan halte: trip terlengkap arah 0 (shape GTFS sudah urut).
- Durasi antar halte: stop_times trip tersebut (dipakai dua arah).
- Frekuensi: gabungan semua pola layanan koridor itu per arah
  (headway efektif = 1 / jumlah(1/headway_i)), dipisah hari kerja/akhir pekan
  lewat calendar.txt. Jendela operasi mengikuti frequencies.txt.
"""

import csv
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "data" / "raw" / "gtfs" / "extracted"
OUT = ROOT / "public" / "data"

CORRIDORS = [str(i) for i in range(1, 15)]
DWELL_SEC = 20
MIN_HEADWAY = 120  # detik; batas bawah headway efektif gabungan

# koridor yang jalurnya melayang (GTFS tidak menyimpan ketinggian):
# 13 = flyover CSW Ciledug–Tendean
ELEVATED_M = {"13": 18.0}

LAT0 = -6.2
R_EARTH = 6371008.8


def to_xy(lon, lat):
    return (
        math.radians(lon) * R_EARTH * math.cos(math.radians(LAT0)),
        math.radians(lat) * R_EARTH,
    )


def dist_km(a, b):
    ax, ay = to_xy(*a[:2])
    bx, by = to_xy(*b[:2])
    return math.hypot(bx - ax, by - ay) / 1000.0


def read(name):
    with open(G / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def hms(s):
    h, m, sec = (int(x) for x in s.split(":"))
    return h * 3600 + m * 60 + sec


def project_forward(coords, cum, pt, min_km):
    """Proyeksikan titik ke garis, hanya pada bagian >= min_km.

    Rute BRT sering pulang-pergi di jalan yang sama (busway median),
    jadi proyeksi bebas bisa 'nyangkut' ke arah pulang. Dengan kursor
    maju (min_km = posisi halte sebelumnya) hasilnya selalu berurutan.
    """
    px, py = to_xy(*pt[:2])
    best = (float("inf"), min_km)
    for i in range(len(coords) - 1):
        if cum[i + 1] < min_km:
            continue
        ax, ay = to_xy(*coords[i][:2])
        bx, by = to_xy(*coords[i + 1][:2])
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        if l2 == 0:
            continue
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
        along = cum[i] + t * (cum[i + 1] - cum[i])
        if along < min_km:
            continue
        d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        if d < best[0]:
            best = (d, along)
    return best[1]


def main():
    routes = {r["route_id"]: r for r in read("routes.txt") if r["route_short_name"] in CORRIDORS}
    trips = [t for t in read("trips.txt") if t["route_id"] in routes]
    trip_by_id = {t["trip_id"]: t for t in trips}

    stops_all = {s["stop_id"]: s for s in read("stops.txt")}
    cal = {c["service_id"]: c for c in read("calendar.txt")}

    # stop_times hanya untuk trip koridor (file besar, saring saat baca)
    st_by_trip = {}
    with open(G / "stop_times.txt", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["trip_id"] in trip_by_id:
                st_by_trip.setdefault(row["trip_id"], []).append(row)
    for v in st_by_trip.values():
        v.sort(key=lambda r: int(r["stop_sequence"]))

    shapes = {}
    with open(G / "shapes.txt", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            shapes.setdefault(row["shape_id"], []).append(row)
    for v in shapes.values():
        v.sort(key=lambda r: int(r["shape_pt_sequence"]))

    freq = read("frequencies.txt")

    line_features, segment_features, station_features, lines_meta = [], [], [], []

    for sn in CORRIDORS:
        route = next(r for r in routes.values() if r["route_short_name"] == sn)
        line_id = f"TJ{sn}"
        rtrips = [t for t in trips if t["route_id"] == route["route_id"]]

        # trip terlengkap per arah
        def best_trip(direction):
            cands = [t for t in rtrips if t.get("direction_id", "0") == direction
                     and t["trip_id"] in st_by_trip and t["shape_id"] in shapes]
            return max(cands, key=lambda t: len(st_by_trip[t["trip_id"]]), default=None)

        rep0 = best_trip("0") or best_trip("1")
        if rep0 is None:
            print(f"{line_id}: tidak ada trip dengan stop_times+shape, lewati")
            continue

        # geometri dari shape (+ ketinggian untuk koridor layang)
        alt = ELEVATED_M.get(sn, 0.0)
        pts = shapes[rep0["shape_id"]]
        coords = []
        for p in pts:
            c = [round(float(p["shape_pt_lon"]), 6), round(float(p["shape_pt_lat"]), 6)]
            if not coords or coords[-1][:2] != c:
                coords.append(c + [alt])
        cum = [0.0]
        for i in range(1, len(coords)):
            cum.append(cum[-1] + dist_km(coords[i - 1], coords[i]))

        # rute melingkar (pulang-pergi jadi satu trip)? ujung shape bertemu
        is_loop = dist_km(coords[0], coords[-1]) < 1.0

        # halte + jarak + offset waktu dari stop_times (kursor maju)
        sts = st_by_trip[rep0["trip_id"]]
        t0 = hms(sts[0]["departure_time"])
        stations, offsets = [], []
        cursor = 0.0
        for j, row in enumerate(sts):
            s = stops_all.get(row["stop_id"])
            if s is None:
                continue
            lon, lat = float(s["stop_lon"]), float(s["stop_lat"])
            cursor = project_forward(coords, cum, (lon, lat), cursor)
            stations.append({
                "code": f"{line_id}-{j + 1:02d}",
                "name": s["stop_name"],
                "lon": round(lon, 6), "lat": round(lat, 6),
                "distAlong": round(cursor, 4),
            })
            offsets.append(hms(row["arrival_time"]) - t0)

        # headway efektif per arah & layanan
        def day_buckets(service_id):
            c = cal.get(service_id)
            if not c:
                return []
            out = []
            if any(c[d] == "1" for d in
                   ("monday", "tuesday", "wednesday", "thursday", "friday")):
                out.append("weekday")
            if c["saturday"] == "1" or c["sunday"] == "1":
                out.append("weekend")
            return out

        # rute melingkar: semua pola digabung jadi satu arah keliling;
        # rute linier: pisah per direction_id
        windows = {}  # (service, direction) -> [rate_sum, min_start, max_end]
        for f_row in freq:
            t = trip_by_id.get(f_row["trip_id"])
            if not t or t["route_id"] != route["route_id"]:
                continue
            d = "0" if is_loop else t.get("direction_id", "0")
            for svc in day_buckets(t["service_id"]):
                key = (svc, d)
                w = windows.setdefault(key, [0.0, 86400, 0])
                w[0] += 1.0 / max(int(f_row["headway_secs"]), 60)
                w[1] = min(w[1], hms(f_row["start_time"]))
                w[2] = max(w[2], hms(f_row["end_time"]))

        # jadwal — format ringkas: pola berhenti ditulis SEKALI per arah,
        # trip individual cuma daftar jam berangkat (starts). Aplikasi
        # mengembangkannya saat load (lihat engine.js). Hemat ~99% ukuran.
        directions = ("0",) if is_loop else ("0", "1")
        for svc in ("weekday", "weekend"):
            blocks = []
            n_trip = 0
            for direction in directions:
                w = windows.get((svc, direction)) or windows.get((svc, "0"))
                if not w:
                    continue
                headway = max(MIN_HEADWAY, int(1.0 / w[0]))
                order = stations if direction == "0" else list(reversed(stations))
                offs = offsets if direction == "0" else \
                    [offsets[-1] - o for o in reversed(offsets)]
                tmpl = []
                for j, st in enumerate(order):
                    dwell = 0 if j in (0, len(order) - 1) else DWELL_SEC
                    tmpl.append({"s": st["code"], "ao": offs[j],
                                 "do": offs[j] + dwell})
                starts = list(range(w[1], w[2] + 1, headway))
                blocks.append({"direction": direction, "dest": order[-1]["code"],
                               "stops": tmpl, "starts": starts})
                n_trip += len(starts)
            (OUT / "timetables" / f"{line_id}_{svc}.json").write_text(
                json.dumps({"lineId": line_id, "service": svc,
                            "generated": True, "source": "gtfs-frequencies",
                            "compact": blocks}),
                encoding="utf-8")
            if svc == "weekday":
                n_wd = n_trip

        color = "#" + route.get("route_color", "888888").lstrip("#")
        long_name = route.get("route_long_name", "")
        line_features.append({
            "type": "Feature",
            "properties": {"lineId": line_id, "color": color, "mode": "brt"},
            "geometry": {"type": "LineString", "coordinates": coords},
        })
        segment_features.append({
            "type": "Feature",
            "properties": {"lineId": line_id, "color": color, "mode": "brt",
                           "level": 1 if alt > 0 else 0},
            "geometry": {"type": "LineString", "coordinates": coords},
        })
        for st in stations:
            station_features.append({
                "type": "Feature",
                "properties": {"lineId": line_id, "code": st["code"],
                               "name": st["name"], "color": color,
                               "distAlong": st["distAlong"]},
                "geometry": {"type": "Point", "coordinates": [st["lon"], st["lat"]]},
            })
        lines_meta.append({
            "id": line_id, "mode": "brt", "operator": "TransJakarta",
            "name": {"id": f"TJ Koridor {sn}: {long_name}",
                     "en": f"TJ Corridor {sn}: {long_name}"},
            "color": color, "lengthKm": round(cum[-1], 3),
            "stations": [{"code": s["code"], "name": s["name"],
                          "distAlong": s["distAlong"]} for s in stations],
        })
        mono = all(a["distAlong"] <= b["distAlong"]
                   for a, b in zip(stations, stations[1:]))
        print(f"{line_id}: {len(stations)} halte, {round(cum[-1], 1)} km"
              f"{' (loop)' if is_loop else ''}, {n_wd} trip/hari kerja"
              f"{'' if mono else '  !! TIDAK MONOTON'}")

    # gabungkan ke file yang ada (buang entri TJ lama dulu — idempoten)
    def merge(path, new_feats):
        data = json.loads((OUT / path).read_text(encoding="utf-8"))
        data["features"] = [f for f in data["features"]
                            if not f["properties"]["lineId"].startswith("TJ")]
        data["features"].extend(new_feats)
        (OUT / path).write_text(json.dumps(data), encoding="utf-8")

    merge("lines.geojson", line_features)
    merge("lines_segments.geojson", segment_features)
    merge("stations.geojson", station_features)
    lj = json.loads((OUT / "lines.json").read_text(encoding="utf-8"))
    lj["lines"] = [l for l in lj["lines"] if not l["id"].startswith("TJ")]
    lj["lines"].extend(lines_meta)
    (OUT / "lines.json").write_text(json.dumps(lj, ensure_ascii=False),
                                    encoding="utf-8")
    print(f"\nselesai: +{len(line_features)} koridor BRT")


if __name__ == "__main__":
    main()
