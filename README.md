# Jabodetabek Transport

> Peta 3D interaktif transportasi umum Jabodetabek (KRL, MRT, LRT, TransJakarta) dengan simulasi posisi kendaraan real-time berbasis jadwal, dibangun dengan Vite + MapLibre GL + deck.gl.

<!-- The README is the front door: what it is, how to run it, where the docs
     are. Depth lives in docs/, not here. -->

## Quickstart

```
npm install
npm run dev
```

Buka `http://localhost:5173`. Full setup: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## Status

v1 sudah berjalan: 10 lin (KRL, MRT, LRT Jakarta, LRT Jabodebek, TransJakarta BRT TJ1–TJ14) tampil di peta dengan simulasi kendaraan berjalan sesuai jadwal; dokumentasi OS baru saja diretrofit.

## Structure

```
src/            # aplikasi frontend (vanilla JS ES modules)
  map/          # setup basemap MapLibre + layer garis/stasiun
  render/       # renderer kendaraan (2d MapLibre debug, 3d deck.gl utama)
  sim/          # jam simulasi WIB + engine posisi kendaraan
  ui/           # panel info, legend, jam, i18n
tools/          # pipeline ETL Python: fetch OSM/GTFS/Comuline -> curate -> build JSON
data/curated/   # metadata lin & parameter layanan hasil kurasi manual
public/data/    # output pipeline: GeoJSON garis/stasiun + jadwal per lin
docs/           # dokumentasi proyek (lihat tabel di bawah)
```

## Documentation

| Doc | What it answers |
|---|---|
| [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) | Why this exists |
| [docs/PRD.md](docs/PRD.md) | Fitur dan kriteria penerimaan |
| [docs/USER_STORIES.md](docs/USER_STORIES.md) | Siapa butuh apa |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Milestone dan urutannya |
| [docs/TASK.md](docs/TASK.md) | What is being worked on |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How it is built |
| [docs/decisions/](docs/decisions/) | ADR — kenapa keputusan struktural diambil |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Setup, run, troubleshoot |
| [docs/TESTING.md](docs/TESTING.md) | Apa yang diuji dan cara menjalankannya |
| [docs/RULES.md](docs/RULES.md) | Deviasi dari standar OS |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Perubahan per versi |
| [docs/memory/STATE.md](docs/memory/STATE.md) | Snapshot sesi kerja terakhir |

---
Scaffolded 2026-07-07 from Claude Engineering OS.
