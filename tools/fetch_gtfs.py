"""Unduh GTFS resmi TransJakarta dan ekstrak ke data/raw/gtfs/extracted/.

Sumber: https://gtfs.transjakarta.co.id/files/file_gtfs.zip
        (URL fetch asli ditemukan lewat halaman feed Transitland
        f-transjakarta~id, operator memperbarui zip ini tanpa jadwal tetap)

build_brt.py membaca folder hasil ekstrak ini. Jalankan dengan --force
untuk mengunduh ulang walau zip sudah ada di cache.
"""

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "gtfs"
ZIP_PATH = RAW_DIR / "transjakarta.zip"
EXTRACT_DIR = RAW_DIR / "extracted"
URL = "https://gtfs.transjakarta.co.id/files/file_gtfs.zip"

REQUIRED_FILES = (
    "routes.txt", "trips.txt", "stop_times.txt", "shapes.txt",
    "frequencies.txt", "calendar.txt", "stops.txt",
)


def main():
    force = "--force" in sys.argv
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if ZIP_PATH.exists() and not force:
        print("GTFS zip sudah ada (cache), lewati unduh. Pakai --force untuk refresh.")
    else:
        print(f"mengunduh {URL} ...")
        # curl.exe dipakai, bukan urllib Python -- lihat catatan yang sama
        # di fetch_krl_comuline.py: beberapa host menolak jabat-tangan TLS
        # dari urllib di Windows tapi menerima curl tanpa masalah.
        r = subprocess.run(
            ["curl.exe", "-sL", "-m", "300", URL, "-o", str(ZIP_PATH),
             "-w", "%{http_code}"],
            capture_output=True, text=True,
        )
        code = r.stdout.strip()
        if r.returncode != 0 or code != "200":
            print(f"!! gagal unduh (curl rc={r.returncode}, http={code})")
            sys.exit(1)
        print(f"  sukses, {ZIP_PATH.stat().st_size // 1024} KB")

    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True)
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(EXTRACT_DIR)

    files = {p.name for p in EXTRACT_DIR.iterdir()}
    print(f"diekstrak: {len(files)} file -> {EXTRACT_DIR}")
    missing = [f for f in REQUIRED_FILES if f not in files]
    if missing:
        print(f"!! file GTFS wajib hilang: {missing}")
        sys.exit(1)


if __name__ == "__main__":
    main()
