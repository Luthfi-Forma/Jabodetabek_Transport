"""Olah data mentah OSM menjadi file siap-pakai untuk aplikasi web.

Input : data/raw/<LINE>.json  (hasil fetch_osm.py)
        data/curated/lines_meta.json  (kurasi manual dari peta FDTJ)
Output: public/data/lines.geojson    (geometri tiap jalur)
        public/data/stations.geojson (titik stasiun + jarak-sepanjang-jalur)
        public/data/lines.json       (metadata jalur untuk aplikasi)

Cara kerja per jalur (tahan terhadap rel ganda / way tak berurutan):
1. Bangun graf rel dari semua way anggota relation.
2. Cocokkan nama stasiun kurasi dengan node stasiun OSM.
3. Cari rute terpendek (Dijkstra) antar stasiun berurutan di graf,
   lalu sambungkan -> satu LineString + jarak km tiap stasiun (distAlong).
"""

import heapq
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "public" / "data"

LAT0 = -6.2  # lintang acuan proyeksi lokal (Jakarta)
R_EARTH = 6371008.8
MAX_STATION_OFFSET_M = 300  # stasiun lebih jauh dari ini dari rel = dicurigai


def to_xy(lon, lat):
    x = math.radians(lon) * R_EARTH * math.cos(math.radians(LAT0))
    y = math.radians(lat) * R_EARTH
    return x, y


def dist_m(a, b):
    ax, ay = to_xy(*a)
    bx, by = to_xy(*b)
    return math.hypot(bx - ax, by - ay)


def normalize(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def dijkstra(graph, coords_of, start, goal):
    """Jalur terpendek start->goal di graf {node: [(tetangga, jarak_m), ...]}."""
    dist = {start: 0.0}
    prev = {}
    pq = [(0.0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            break
        if d > dist.get(u, float("inf")):
            continue
        for v, w in graph.get(u, ()):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if goal not in dist:
        return None, float("inf")
    path = [goal]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()
    return path, dist[goal]


def process_line(meta, raw):
    line_id = meta["id"]
    nodes, ways, relation = {}, {}, None
    for el in raw["elements"]:
        if el["type"] == "node":
            nodes[el["id"]] = el
        elif el["type"] == "way":
            ways[el["id"]] = el
        elif el["type"] == "relation":
            relation = el

    # 1) graf rel dari way anggota (peron dikecualikan)
    graph = {}

    def add_edge(a, b):
        na, nb = nodes[a], nodes[b]
        w = dist_m((na["lon"], na["lat"]), (nb["lon"], nb["lat"]))
        graph.setdefault(a, []).append((b, w))
        graph.setdefault(b, []).append((a, w))

    for m in relation["members"]:
        if m["type"] != "way" or "platform" in m.get("role", ""):
            continue
        w = ways.get(m["ref"])
        if not w:
            continue
        for i in range(len(w["nodes"]) - 1):
            add_edge(w["nodes"][i], w["nodes"][i + 1])

    # jembatani node yang berdekatan (<= 20 m) tapi tak tersambung —
    # data OSM sering tanpa wesel/crossover antar rel ganda, sehingga
    # rute bisa "terjebak" di satu rel dan memutar jauh
    BRIDGE_M = 20.0
    graph_nodes = list(graph.keys())
    xy = {nid: to_xy(nodes[nid]["lon"], nodes[nid]["lat"]) for nid in graph_nodes}
    cell = 25.0
    grid = {}
    for nid in graph_nodes:
        gx, gy = int(xy[nid][0] // cell), int(xy[nid][1] // cell)
        grid.setdefault((gx, gy), []).append(nid)
    for nid in graph_nodes:
        gx, gy = int(xy[nid][0] // cell), int(xy[nid][1] // cell)
        linked = {v for v, _ in graph[nid]}
        for cx in (gx - 1, gx, gx + 1):
            for cy in (gy - 1, gy, gy + 1):
                for other in grid.get((cx, cy), ()):
                    if other <= nid or other in linked:
                        continue
                    d = math.hypot(xy[nid][0] - xy[other][0],
                                   xy[nid][1] - xy[other][1])
                    if d <= BRIDGE_M:
                        graph[nid].append((other, d))
                        graph[other].append((nid, d))

    # 2) kandidat node stasiun bernama
    candidates = {}
    for el in raw["elements"]:
        if el["type"] != "node":
            continue
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        if tags.get("railway") in ("station", "halt", "stop") or \
                tags.get("public_transport") in ("station", "stop_position"):
            candidates.setdefault(normalize(name), []).append(
                (name, el["lon"], el["lat"])
            )

    # pencocokan nama: pas persis -> awalan -> substring
    matched, unmatched = {}, []
    for st in meta["stations"]:
        if "lon" in st and "lat" in st:
            matched[st["code"]] = (st["lon"], st["lat"], "manual")
            continue
        target = normalize(st.get("osmName", st["name"]))
        found = None
        if target in candidates:
            found = candidates[target][0]
        else:
            pref = sorted((k for k in candidates if k.startswith(target)), key=len)
            if pref:
                found = candidates[pref[0]][0]
            else:
                sub = [k for k in candidates if target in k]
                if len(sub) == 1:
                    found = candidates[sub[0]][0]
        if found:
            matched[st["code"]] = (found[1], found[2], found[0])
        else:
            unmatched.append(st)

    if unmatched:
        print(f"  !! {line_id}: stasiun tak ketemu di OSM: "
              f"{[s['name'] for s in unmatched]}")
        print(f"     kandidat: "
              f"{sorted(set(n for v in candidates.values() for n, _, _ in v))}")

    # 3) node graf terdekat per stasiun, lalu Dijkstra antar stasiun berurutan
    def nearest_graph_node(pt):
        best, best_d = None, float("inf")
        px, py = to_xy(*pt)
        for nid in graph_nodes:
            n = nodes[nid]
            nx, ny = to_xy(n["lon"], n["lat"])
            d = math.hypot(px - nx, py - ny)
            if d < best_d:
                best, best_d = nid, d
        return best, best_d

    anchor = {}
    for st in meta["stations"]:
        if st["code"] not in matched:
            continue
        lon, lat, osm_name = matched[st["code"]]
        nid, off = nearest_graph_node((lon, lat))
        if off > MAX_STATION_OFFSET_M:
            print(f"  !! {line_id} {st['name']}: {round(off)} m dari rel "
                  f"(node OSM: {osm_name})")
        anchor[st["code"]] = nid

    codes = [s["code"] for s in meta["stations"] if s["code"] in anchor]
    coords, stations, broken = [], [], 0
    cum_km = 0.0

    def push_coord(nid):
        nonlocal cum_km
        n = nodes[nid]
        c = [round(n["lon"], 6), round(n["lat"], 6)]
        if coords:
            prev = coords[-1]
            if prev == c:
                return
            cum_km += dist_m(prev, c) / 1000.0
        coords.append(c)

    push_coord(anchor[codes[0]])
    meta_by_code = {s["code"]: s for s in meta["stations"]}
    stations.append({"code": codes[0], "name": meta_by_code[codes[0]]["name"],
                     "lon": coords[0][0], "lat": coords[0][1], "distAlong": 0.0})

    for a, b in zip(codes, codes[1:]):
        path, d = dijkstra(graph, nodes, anchor[a], anchor[b])
        if path is None:
            print(f"  !! {line_id}: tidak ada jalur rel {a} -> {b} di graf!")
            broken += 1
            path = [anchor[a], anchor[b]]  # garis lurus darurat
        for nid in path[1:]:
            push_coord(nid)
        n = nodes[anchor[b]]
        stations.append({"code": b, "name": meta_by_code[b]["name"],
                         "lon": round(n["lon"], 6), "lat": round(n["lat"], 6),
                         "distAlong": round(cum_km, 4)})

    order = [s["distAlong"] for s in stations]
    if order != sorted(order):
        print(f"  !! {line_id}: distAlong tidak monoton naik: {order}")
        broken += 1

    # jarak antar stasiun yang tak wajar = indikasi rute memutar
    for s1, s2 in zip(stations, stations[1:]):
        gap = s2["distAlong"] - s1["distAlong"]
        straight = dist_m((s1["lon"], s1["lat"]), (s2["lon"], s2["lat"])) / 1000.0
        if gap > max(10.0, 3.0 * straight):
            print(f"  !! {line_id}: {s1['name']} -> {s2['name']} = {gap:.1f} km "
                  f"(garis lurus cuma {straight:.1f} km) — rute memutar?")
            broken += 1

    return {
        "coords": coords,
        "length_km": round(cum_km, 3),
        "stations": stations,
        "n_problems": len(unmatched) + broken,
    }


def main():
    meta_all = json.loads(
        (ROOT / "data" / "curated" / "lines_meta.json").read_text(encoding="utf-8")
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    line_features, station_features, lines_meta_out = [], [], []
    problems = 0

    for meta in meta_all["lines"]:
        line_id = meta["id"]
        raw_path = RAW_DIR / f"{line_id}.json"
        if not raw_path.exists():
            print(f"{line_id}: data mentah belum ada, jalankan fetch_osm.py dulu")
            problems += 1
            continue
        print(f"{line_id}: memproses ...")
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        result = process_line(meta, raw)
        problems += result["n_problems"]
        print(f"  {len(result['coords'])} titik, {result['length_km']} km, "
              f"{len(result['stations'])}/{len(meta['stations'])} stasiun")

        line_features.append({
            "type": "Feature",
            "properties": {
                "lineId": line_id,
                "color": meta["color"],
                "mode": meta["mode"],
            },
            "geometry": {"type": "LineString", "coordinates": result["coords"]},
        })
        for s in result["stations"]:
            station_features.append({
                "type": "Feature",
                "properties": {
                    "lineId": line_id,
                    "code": s["code"],
                    "name": s["name"],
                    "color": meta["color"],
                    "distAlong": s["distAlong"],
                },
                "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
            })
        lines_meta_out.append({
            "id": line_id,
            "mode": meta["mode"],
            "operator": meta["operator"],
            "name": meta["name"],
            "color": meta["color"],
            "lengthKm": result["length_km"],
            "stations": [
                {"code": s["code"], "name": s["name"], "distAlong": s["distAlong"]}
                for s in result["stations"]
            ],
        })

    (OUT_DIR / "lines.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": line_features}),
        encoding="utf-8")
    (OUT_DIR / "stations.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": station_features}),
        encoding="utf-8")
    (OUT_DIR / "lines.json").write_text(
        json.dumps({"lines": lines_meta_out}, ensure_ascii=False),
        encoding="utf-8")

    print(f"\nselesai: {len(line_features)} jalur, {len(station_features)} stasiun, "
          f"{problems} masalah")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
