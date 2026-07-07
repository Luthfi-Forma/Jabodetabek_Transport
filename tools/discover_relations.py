"""Cari relation ID rute kereta di area Jabodetabek dari OpenStreetMap.

Sekali pakai: hasilnya dipakai untuk mengisi tools/osm_relations.json
(relation ID di-pin manual supaya pipeline tidak bergantung pada
pencocokan nama yang rapuh).
"""

import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# bbox Jabodetabek: selatan, barat, utara, timur
BBOX = "-6.85,106.3,-5.95,107.35"

QUERY = f"""
[out:json][timeout:60];
relation["type"="route"]["route"~"subway|light_rail|train|railway"]({BBOX});
out tags;
"""


def main():
    req = urllib.request.Request(
        OVERPASS_URL,
        data=QUERY.encode(),
        headers={"User-Agent": "mini-jakarta-3d data pipeline"},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.load(resp)

    rows = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        rows.append(
            {
                "id": el["id"],
                "route": tags.get("route", ""),
                "name": tags.get("name", ""),
                "ref": tags.get("ref", ""),
                "operator": tags.get("operator", ""),
                "from": tags.get("from", ""),
                "to": tags.get("to", ""),
            }
        )

    rows.sort(key=lambda r: (r["route"], r["name"]))
    for r in rows:
        print(
            f"{r['id']:>12}  {r['route']:<10} {r['name'][:70]:<70} "
            f"[{r['from'][:20]} -> {r['to'][:20]}] op={r['operator'][:30]}"
        )
    print(f"\ntotal: {len(rows)} relations")


if __name__ == "__main__":
    main()
