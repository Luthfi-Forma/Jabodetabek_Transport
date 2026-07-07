# Architecture — Jabodetabek Transport

- Updated: 2026-07-07
- Process: `C:\Users\Luthfi\Documents\Claude Code\Claude Engineering OS\standards\architecture\system-design-process.md`

## System context

Aplikasi adalah *static site* murni: tidak ada backend atau database di
produksi. Sebuah pipeline ETL offline (skrip Python di `tools/`) mengambil
data mentah dari tiga sumber eksternal — OpenStreetMap Overpass API (geometri
rute & stasiun), feed GTFS resmi TransJakarta, dan API pihak ketiga
comuline.com (jadwal KRL) — lalu mengkurasinya menjadi file GeoJSON/JSON
statis di `public/data/`. Browser pengguna memuat file-file statis ini
langsung; seluruh logika simulasi posisi kendaraan berjalan di sisi klien.

```
OSM Overpass ─┐
GTFS TransJakarta ─┼─> tools/*.py (offline ETL) ─> public/data/*.json ─> browser (Vite app)
Comuline API ─┘                                                             │
                                                                    MapLibre GL + deck.gl
```

## Tech stack

| Layer | Choice | Why / ADR |
|---|---|---|
| Build tool | Vite | Dev server cepat + code-splitting bawaan untuk memisahkan chunk 3D |
| Bahasa frontend | Vanilla JS (ES modules) | Deviasi dari default TypeScript OS untuk gis-app — lihat [decisions/ADR-001-vanilla-js-over-typescript.md](decisions/ADR-001-vanilla-js-over-typescript.md) |
| Peta dasar | MapLibre GL + basemap CartoDB Dark Matter | Gratis, tanpa token, gaya gelap sesuai kebutuhan visual |
| Render 2D (garis/stasiun) | Layer MapLibre GL native | Cukup untuk garis statis & titik stasiun |
| Render 3D (kendaraan) | deck.gl (`SimpleMeshLayer`) + luma.gl (`CubeGeometry`) | Balok kendaraan 3D dengan performa GPU; di-dynamic-import agar tidak menghalangi render peta pertama kali |
| Simulasi | Modul JS custom (`src/sim/`) | Jam WIB independen dari zona waktu PC pengguna + interpolasi posisi berbasis jadwal |
| ETL data | Python 3 (stdlib + `requests`-style fetch) | Skrip sekali-jalan, tidak perlu framework |
| Penyimpanan data | File statis JSON/GeoJSON di `public/data/` | Tidak ada database — semua data bisa dibangun ulang dari sumber |

## Components

### `src/map/`
Setup basemap MapLibre (`initMap.js`), layer garis dengan gaya elevasi
(`lineLayers.js`), dan layer stasiun yang bisa diklik (`stationLayer.js`).
Tidak boleh menaruh logika simulasi di sini — hanya render statis + event
klik yang diteruskan ke `src/ui/`.

### `src/render/`
Renderer kendaraan: `vehicles2d.js` (lingkaran MapLibre, mode debug/cadangan)
dan `vehicles3d.js` (balok deck.gl, mode utama — lihat `CONFIG.vehicleRenderer`
di `src/config.js`). Menerima posisi terhitung dari `src/sim/engine.js`,
tidak menghitung posisi sendiri.

### `src/sim/`
`clock.js`: jam simulasi WIB, bisa dipercepat/dilompat via
`__clock.set({ mult, at })` dari konsol browser untuk pengujian.
`engine.js`: menghitung posisi tiap kendaraan aktif per tick berdasarkan
jadwal (`public/data/timetables/*.json`) dengan easing kubik antar-stasiun;
menangani kasus jadwal lintas tengah malam dengan mengecek `t` dan `t+24h`.

### `src/ui/`
Panel info (`infoPanel.js`) untuk detail stasiun/kendaraan yang diklik,
legend (`legend.js`) dengan toggle per lin, tampilan jam (`clockDisplay.js`),
dan i18n (`i18n.js`) untuk UI dwibahasa ID/EN.

### `tools/`
Pipeline ETL Python, dijalankan offline/manual (tidak ada CI terjadwal saat
ini): `fetch_osm.py`, `fetch_gtfs.py`, `fetch_krl_comuline.py` (akuisisi data
mentah) → `discover_relations.py`, `build_geojson.py`, `build_brt.py`
(kurasi & transformasi geometri, memakai `data/curated/lines_meta.json` dan
`tools/osm_relations.json`) → `build_timetables.py` (jadwal sintetis/nyata
memakai `data/curated/service_params.json`) → `refresh_all.py`
(orkestrator seluruh rantai, `--full` untuk rebuild geometri juga).

## Data flow

1. **Refresh data (offline, manual)**: `python tools/refresh_all.py [--full]`
   menjalankan rantai fetch → curate → build, menghasilkan
   `public/data/lines.geojson`, `lines_segments.geojson`, `stations.geojson`,
   `lines.json`, dan `timetables/{lineId}_{weekday,weekend}.json`.
2. **Muat aplikasi**: `src/main.js` memuat file-file statis di atas,
   memanggil `initMap.js` untuk setup basemap + layer garis/stasiun.
3. **Tick simulasi (client, tiap frame/detik)**: `src/sim/clock.js` memberi
   waktu simulasi WIB saat ini → `src/sim/engine.js` mencocokkannya dengan
   jadwal per lin (weekday/weekend dari `serviceDay()`) → menghitung posisi
   interpolasi tiap kendaraan aktif → `src/render/vehicles3d.js` (atau
   `vehicles2d.js`) menggambar ulang posisi tersebut di peta.

## Deployment shape

Belum ada — proyek belum pernah di-deploy ke hosting publik. Build produksi
(`npm run build` → `dist/`) sudah bisa dijalankan sebagai static site, tapi
target hosting belum dipilih. Lihat `docs/ROADMAP.md` M2 dan `docs/TASK.md`
T-01–T-03.

## Decisions

See [decisions/](decisions/) for all ADRs.

## Open questions

- Target hosting/deployment — putuskan sebelum milestone M2 (`docs/ROADMAP.md`).
- Migrasi TypeScript vs bertahan vanilla JS — putuskan saat proyek butuh
  kontributor tambahan (lihat ADR-001).
- Strategi test otomatis — putuskan saat memulai milestone M3.
