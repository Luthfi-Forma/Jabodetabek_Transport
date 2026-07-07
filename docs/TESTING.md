# Testing — Jabodetabek Transport

- Updated: 2026-07-07
- Baseline: `C:\Users\Luthfi\Documents\Claude Code\Claude Engineering OS\standards\testing.md` (this doc records the
  project-specific plan, not the general rules)

## How to run

Belum ada test otomatis untuk dijalankan. Verifikasi saat ini seluruhnya
manual:

```
npm run dev
```

Lalu periksa secara visual di browser (lihat "What we test" di bawah).

## What we test, per layer

<!-- Jujur: belum ada lapis test otomatis sama sekali. -->

| Layer | Tool | What is covered | Target |
|---|---|---|---|
| unit | — | tidak ada | belum ada target — lihat `docs/ROADMAP.md` M3 |
| integration | — | tidak ada | belum ada target |
| e2e / manual | browser + konsol | render peta, seluruh 10 lin tampil, klik stasiun/kendaraan menampilkan info benar, `__clock.set()` mengubah simulasi sesuai harapan, kasus lintas tengah malam tidak melompat | tiap kali `src/sim/`, `src/map/`, atau `src/render/` diubah |

## Test data

Untuk verifikasi manual, pakai jadwal & geometri nyata yang sudah ada di
`public/data/` (bukan data sintetis) — semuanya sudah berbasis koordinat dan
jadwal Jabodetabek yang sesungguhnya, hasil kurasi dari
`2026-06a-Peta-Integrasi-Jakarta-FDTJ-Web.pdf` dan sumber-sumber di
`docs/PROJECT_BRIEF.md` References.

## Known gaps

- Tidak ada test unit untuk `src/sim/engine.js` (interpolasi posisi, kasus
  lintas tengah malam) — kandidat pertama untuk M3, dicatat sebagai risiko
  di `docs/memory/DEBT.md`.
- Tidak ada test untuk skrip `tools/*.py` (mis. apakah `build_geojson.py`
  menghasilkan path yang benar dari graph OSM) — belum ada rencana konkret,
  lihat `docs/ROADMAP.md` Icebox.
