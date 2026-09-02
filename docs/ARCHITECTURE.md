# Arsitektur

## Gambaran besarnya

Ini situs statis murni — nggak ada backend atau database di produksi.

Ada pipeline ETL offline (skrip Python di `tools/`) yang narik data mentah
dari tiga sumber: OpenStreetMap Overpass API (geometri rute & stasiun), feed
GTFS resmi TransJakarta, dan API pihak ketiga comuline.com (jadwal KRL).
Hasilnya dikurasi jadi file GeoJSON/JSON statis di `public/data/`.

Browser tinggal muat file-file itu. Semua logika simulasi posisi kendaraan
jalan di sisi klien.

```
OSM Overpass ─┐
GTFS TransJakarta ─┼─> tools/*.py (ETL offline) ─> public/data/*.json ─> browser (app Vite)
Comuline API ─┘                                                             │
                                                                    MapLibre GL + deck.gl
```

## Pakai apa aja

| Bagian | Pilihan | Alasannya |
|---|---|---|
| Build tool | Vite | Dev server-nya kenceng, code-splitting udah bawaan buat misahin chunk 3D |
| Bahasa frontend | Vanilla JS (ES modules) | Lihat [ADR-001](decisions/ADR-001-vanilla-js-over-typescript.md) |
| Peta dasar | MapLibre GL + basemap CartoDB Dark Matter | Gratis, nggak perlu token, gayanya gelap sesuai kebutuhan |
| Render 2D (garis/stasiun) | Layer MapLibre GL native | Udah cukup buat garis statis sama titik stasiun |
| Render 3D (kendaraan) | deck.gl (`SimpleMeshLayer`) + luma.gl (`CubeGeometry`) | Balok kendaraan 3D yang ngandelin GPU; di-dynamic-import biar nggak ngeblok render peta pertama |
| Simulasi | Modul JS sendiri (`src/sim/`) | Jam WIB yang nggak ikut zona waktu PC pengguna + interpolasi posisi berbasis jadwal |
| ETL data | Python 3 | Skrip sekali jalan, nggak perlu framework |
| Simpan data | File statis JSON/GeoJSON di `public/data/` | Nggak ada database — semua data bisa dibangun ulang dari sumbernya |

## Komponennya

### `src/map/`

Setup basemap MapLibre (`initMap.js`), layer garis dengan gaya per elevasi
(`lineLayers.js`), dan layer stasiun yang bisa diklik (`stationLayer.js`).

Jangan taruh logika simulasi di sini — cuma render statis dan event klik yang
diteruskan ke `src/ui/`.

### `src/render/`

Renderer kendaraan: `vehicles2d.js` (lingkaran MapLibre, buat mode debug atau
cadangan) dan `vehicles3d.js` (balok deck.gl, mode utama — atur lewat
`CONFIG.vehicleRenderer` di `src/config.js`).

Modul ini terima posisi yang udah dihitung dari `src/sim/engine.js`. Dia nggak
ngitung posisi sendiri.

### `src/sim/`

`clock.js` — jam simulasi WIB. Bisa dipercepat atau dilompat lewat
`__clock.set({ mult, at })` dari konsol browser buat keperluan pengujian.

`engine.js` — ngitung posisi tiap kendaraan aktif per tick berdasarkan jadwal
di `public/data/timetables/*.json`, pakai easing kubik antar stasiun. Jadwal
yang lewat tengah malam ditangani dengan ngecek `t` dan `t+24h` sekaligus.

### `src/ui/`

Panel info (`infoPanel.js`) buat detail stasiun/kendaraan yang diklik, legenda
(`legend.js`) dengan toggle per lin, tampilan jam (`clockDisplay.js`), dan
i18n (`i18n.js`) buat UI dwibahasa ID/EN.

### `tools/`

Pipeline ETL Python, dijalanin manual (belum ada CI terjadwal):

- Ambil data mentah — `fetch_osm.py`, `fetch_gtfs.py`, `fetch_krl_comuline.py`
- Kurasi & transformasi geometri — `discover_relations.py`, `build_geojson.py`,
  `build_brt.py` (pakai `data/curated/lines_meta.json` dan
  `tools/osm_relations.json`)
- Bangun jadwal — `build_timetables.py` (pakai `data/curated/service_params.json`)
- Orkestrator seluruh rantai — `refresh_all.py` (`--full` buat rebuild
  geometri juga)

## Alur datanya

1. **Refresh data (offline, manual).** `python tools/refresh_all.py [--full]`
   jalanin rantai fetch → kurasi → build. Hasilnya
   `public/data/lines.geojson`, `lines_segments.geojson`, `stations.geojson`,
   `lines.json`, dan `timetables/{lineId}_{weekday,weekend}.json`.
2. **Aplikasi dimuat.** `src/main.js` muat file-file di atas, terus manggil
   `initMap.js` buat setup basemap + layer garis/stasiun.
3. **Tick simulasi (di klien, tiap frame).** `src/sim/clock.js` ngasih waktu
   WIB saat ini → `src/sim/engine.js` cocokin sama jadwal per lin
   (weekday/weekend dari `serviceDay()`) → hitung posisi interpolasi tiap
   kendaraan aktif → `src/render/vehicles3d.js` (atau `vehicles2d.js`)
   gambar ulang posisinya di peta.

## Deploy

Belum pernah di-deploy ke hosting publik. Build produksi (`npm run build` →
`dist/`) udah bisa jalan sebagai situs statis, tapi target hostingnya belum
dipilih.

## Keputusan

Lihat [decisions/](decisions/).
