r"""Perbarui semua data yang sumbernya bisa berubah dari waktu ke waktu.

Pemakaian:
  python tools/refresh_all.py          -> refresh jadwal & BRT (rutin)
  python tools/refresh_all.py --full   -> ikut segarkan geometri rel dari
                                           OpenStreetMap (jarang perlu --
                                           hanya kalau ada perubahan
                                           rute/stasiun kereta)

Urutan penting: build_geojson.py MENIMPA lines.json dari nol (rel saja),
sedangkan build_brt.py MENGGABUNGKAN data BRT ke file yang sama. Jadi
langkah rel (kalau --full) harus jalan sebelum langkah BRT.

Cocok dijadwalkan lewat Windows Task Scheduler, mis. tiap Senin jam 03:00:
  schtasks /create /tn "mini-jakarta-3d refresh" /sc weekly /d MON /st 03:00 ^
    /tr "python \"C:\...\Jabodetabek_Transport\tools\refresh_all.py\""
"""

import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TOOLS = Path(__file__).resolve().parent


def run(label, script, *args):
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    t0 = time.time()
    r = subprocess.run([sys.executable, str(TOOLS / script), *args])
    dt = time.time() - t0
    ok = r.returncode == 0
    print(f"-> {'OK' if ok else 'GAGAL'} ({dt:.0f} detik)")
    return ok


def main():
    args = set(sys.argv[1:])
    unknown = args - {"--full"}
    if unknown:
        print(f"!! argumen tak dikenal: {sorted(unknown)} (hanya --full yang valid)")
        print(__doc__)
        sys.exit(2)
    full = "--full" in args
    results = []

    if full:
        results.append(("Geometri rel (OSM)",
                         run("Unduh ulang geometri rel dari OpenStreetMap",
                             "fetch_osm.py", "--force")))
        results.append(("GeoJSON rel",
                         run("Bangun ulang lines/stations GeoJSON (rel)",
                             "build_geojson.py")))

    results.append(("Jadwal headway",
                     run("Bangun ulang jadwal headway (MRT/LRT/KA Bandara + fallback KRL)",
                         "build_timetables.py")))
    results.append(("GTFS TransJakarta",
                     run("Unduh ulang feed GTFS TransJakarta",
                         "fetch_gtfs.py", "--force")))
    results.append(("Koridor BRT",
                     run("Bangun ulang 14 koridor BRT dari GTFS",
                         "build_brt.py")))
    results.append(("Jadwal KRL asli",
                     run("Unduh ulang jadwal KRL asli dari comuline",
                         "fetch_krl_comuline.py", "--force")))

    print(f"\n{'=' * 60}\nRINGKASAN\n{'=' * 60}")
    for name, ok in results:
        print(f"  [{'OK' if ok else 'GAGAL'}] {name}")
    failed = [name for name, ok in results if not ok]
    if failed:
        print(f"\n!! {len(failed)} langkah gagal: {', '.join(failed)}")
        sys.exit(1)
    print("\nsemua data berhasil diperbarui.")


if __name__ == "__main__":
    main()
