# Development Guide — Jabodetabek Transport

- Updated: 2026-07-07

## Setup (once)

1. Install Node.js (untuk Vite) dan Python 3.8+ (untuk pipeline data di
   `tools/` — hanya memakai stdlib, tidak ada `requirements.txt`).
2. Clone repo, lalu di root proyek:
   ```
   npm install
   ```
3. (Opsional) Bangun ulang data dari sumber — lihat "Refresh data" di bawah.
   Data hasil build sudah tersedia di `public/data/`, jadi langkah ini tidak
   wajib untuk sekadar menjalankan aplikasi.

## Run

```
npm run dev
```

Buka `http://localhost:5173`. Claude Code dapat menjalankan ini lewat
preview tools karena `.claude/launch.json` sudah berisi konfigurasi `dev`
(port 5173) dan `preview` (port 5174, untuk `npm run preview` setelah build).

## Common tasks

### Refresh data (rutin — jadwal & BRT)

```
python tools/refresh_all.py
```

Mengunduh ulang jadwal KRL (comuline), feed GTFS TransJakarta, dan membangun
ulang jadwal headway + koridor BRT.

### Refresh data (penuh — termasuk geometri rel)

```
python tools/refresh_all.py --full
```

Ikut mengunduh ulang geometri rel dari OpenStreetMap Overpass sebelum
langkah rutin di atas. Hanya perlu dijalankan bila ada perubahan
rute/stasiun kereta di lapangan. **Urutan penting**: langkah geometri
(`build_geojson.py`) menimpa `lines.json` dari nol, sedangkan langkah BRT
(`build_brt.py`) menggabungkan data BRT ke file yang sama — jangan jalankan
`build_brt.py` sebelum `build_geojson.py` bila memakai `--full`
(`refresh_all.py` sudah menjaga urutan ini secara otomatis).

### Build produksi

```
npm run build
```

Menghasilkan `dist/` (static site murni). Lihat `docs/ROADMAP.md` M2 untuk
status keputusan hosting.

### Run tests

```
<!-- Belum ada test otomatis — lihat docs/TESTING.md dan docs/ROADMAP.md M3. -->
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Render 3D kendaraan terasa lambat/patah saat pertama kali load | deck.gl/luma.gl di-dynamic-import agar tidak menghalangi render peta dasar; chunk `vendor-deck` baru dimuat setelah peta tampil | Normal — tunggu beberapa ratus ms; kalau ingin cek render 2D lebih dulu, set `vehicleRenderer: '2d'` di `src/config.js` |
| Jadwal KRL/GTFS gagal diunduh saat `refresh_all.py` | Sumber pihak ketiga (comuline.com) atau feed resmi TransJakarta sedang down/berubah format | Cek koneksi & URL di `tools/fetch_krl_comuline.py` / `tools/fetch_gtfs.py`; data lama di `public/data/` tetap berfungsi sampai refresh berhasil |
| Kendaraan "lompat" di sekitar tengah malam | Jadwal lintas tengah malam butuh pengecekan `t` dan `t+24h` sekaligus | Pastikan logika di `src/sim/engine.js` tidak diubah tanpa mempertahankan pengecekan dua waktu ini |
