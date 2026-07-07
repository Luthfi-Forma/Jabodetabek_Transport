# Roadmap — Jabodetabek Transport

- Updated: 2026-07-07

<!-- The roadmap answers "what order and why". Tasks live in TASK.md, not here. -->

## Milestones

| # | Milestone | Outcome (verifiable) | Status |
|---|---|---|---|
| M1 | Peta 3D interaktif v1 | Semua 10 lin (KRL, MRT, LRT Jakarta, LRT Jabodebek, TransJakarta BRT) tampil di peta dengan kendaraan bersimulasi sesuai jadwal, panel info, legend, UI dwibahasa | done |
| M2 | Siap deploy publik | Target hosting dipilih, `docs/DEPLOYMENT.md` + `docs/SECURITY.md` ditulis, build produksi berjalan di URL publik | planned |
| M3 | Jaring pengaman otomatis | Ada setidaknya satu lapis test otomatis (unit untuk `src/sim/engine.js`, atau e2e render peta) berjalan di CI | planned |

## Current focus

M1 sudah selesai (aplikasi sudah bisa dijalankan dan berfungsi penuh secara
lokal). Fokus berikutnya adalah M2: memilih target hosting dan menuliskan
`DEPLOYMENT.md`/`SECURITY.md` yang saat ini sengaja belum ada karena belum
ada keputusan deployment (lihat `docs/PROJECT_BRIEF.md` Non-goals).

## Phase detail

### M2 — Siap deploy publik

- Pilih target hosting (mis. GitHub Pages, Vercel, Netlify) — pertimbangkan
  bahwa build adalah static site murni (`npm run build` -> `dist/`).
- Tulis `docs/DEPLOYMENT.md` (proses build & rilis) dan `docs/SECURITY.md`
  (tidak ada auth/data pengguna, tapi tetap perlu daftar dependensi
  eksternal: CartoDB basemap, Overpass, GTFS TransJakarta, Comuline API).
- Tentukan apakah pipeline data (`tools/refresh_all.py`) perlu dijadwalkan
  otomatis (mis. cron/CI) atau tetap manual.

### M3 — Jaring pengaman otomatis

- Tambahkan test untuk `src/sim/engine.js` (interpolasi posisi, kasus lintas
  tengah malam) — kandidat lapis unit pertama.
- Evaluasi kebutuhan test end-to-end untuk render peta dasar.

## Icebox

- Migrasi ke TypeScript (default stack OS untuk gis-app) — lihat
  `docs/decisions/ADR-001-vanilla-js-over-typescript.md` untuk alasan
  bertahan di vanilla JS saat ini.
- Data posisi kendaraan live (GPS operator) sebagai pengganti simulasi
  berbasis jadwal.
- Dukungan moda selain rel & BRT (angkot, ojek online).
