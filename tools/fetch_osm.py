"""Unduh data mentah relation OSM (jalur + stasiun) ke data/raw/.

Pakai cache: file yang sudah ada tidak diunduh ulang.
Jalankan ulang dengan --force untuk refresh.
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def fetch_relation(rel_id: int) -> dict:
    query = f"[out:json][timeout:120];relation({rel_id});(._;>;);out body;"
    req = urllib.request.Request(
        OVERPASS_URL,
        data=query.encode(),
        headers={"User-Agent": "mini-jakarta-3d data pipeline"},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (429, 504) and attempt < 4:
                wait = 30 * (attempt + 1)
                print(f"  server sibuk ({e.code}), tunggu {wait} detik ...")
                time.sleep(wait)
            else:
                raise


def main():
    force = "--force" in sys.argv
    relations = json.loads(
        (ROOT / "tools" / "osm_relations.json").read_text(encoding="utf-8")
    )["relations"]
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for line_id, rel_id in relations.items():
        out_path = RAW_DIR / f"{line_id}.json"
        if out_path.exists() and not force:
            print(f"{line_id}: sudah ada (cache), lewati")
            continue
        print(f"{line_id}: mengunduh relation {rel_id} ...")
        data = fetch_relation(rel_id)
        n_nodes = sum(1 for e in data["elements"] if e["type"] == "node")
        n_ways = sum(1 for e in data["elements"] if e["type"] == "way")
        print(f"  -> {n_nodes} node, {n_ways} way")
        out_path.write_text(json.dumps(data), encoding="utf-8")
        time.sleep(8)  # sopan ke server Overpass

    print("selesai.")


if __name__ == "__main__":
    main()
