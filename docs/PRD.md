# PRD — Jabodetabek Transport

- Date: 2026-07-07
- Source: [PROJECT_BRIEF.md](PROJECT_BRIEF.md)
- Status: Draft
<!-- Fitur di bawah sudah dibangun (v1); PRD ini mendokumentasikan apa yang
     ada supaya perubahan di masa depan punya baseline yang jelas. -->

## Overview

Aplikasi web satu halaman yang merender peta 3D interaktif jaringan transit
Jabodetabek, dengan kendaraan yang bergerak sepanjang rute mengikuti jadwal
nyata/sintetis. Ditujukan untuk penggemar transportasi umum dan pengembang
yang tertarik pada pola integrasi data transit multi-sumber.

## Personas

- **Rian, penggemar transportasi umum** — ingin melihat bagaimana seluruh
  jaringan KRL/MRT/LRT/BRT Jabodetabek "hidup" sepanjang hari, termasuk jam
  sibuk pagi/sore, tanpa harus berada di lapangan.
- **Sari, pengembang GIS** — ingin mempelajari/mereplikasi pola pipeline data
  (OSM + GTFS + jadwal operator → GeoJSON + simulasi klien) untuk proyek
  pemetaan transit lain.

## Features

| ID | Feature | Priority | Acceptance criteria |
|---|---|---|---|
| F-01 | Render garis & stasiun 3D di peta | P1 | Semua 10 lin tampil dengan warna dan gaya elevasi (glow/solid/dashed) yang benar; klik stasiun menampilkan nama + kode + lin yang melayani |
| F-02 | Simulasi posisi kendaraan berbasis jadwal | P1 | Kendaraan bergerak di sepanjang rute sesuai `public/data/timetables/*.json`, dengan easing kubik antar-stasiun; kasus lintas tengah malam (t dan t+24h) ditangani tanpa lompatan posisi |
| F-03 | Jam simulasi WIB + kontrol pengujian | P1 | Jam tampil di UI mengikuti WIB; `__clock.set({ mult, at })` di konsol browser mengubah kecepatan/waktu simulasi secara langsung |
| F-04 | Info panel kendaraan/stasiun | P1 | Klik kendaraan menampilkan tujuan + stasiun berikutnya; klik stasiun menampilkan daftar lin yang singgah |
| F-05 | Legend dengan toggle per lin | P2 | Legend bisa dilipat/dibuka; setiap lin punya chip warna dan toggle tampil/sembunyi yang langsung memengaruhi layer peta |
| F-06 | UI dwibahasa (ID/EN) | P2 | Seluruh label UI berganti bahasa saat pengguna beralih antara Indonesia/Inggris |
| F-07 | Pipeline data offline yang bisa dijalankan ulang | P1 | `python tools/refresh_all.py` menghasilkan ulang seluruh `public/data/**` tanpa error dari sumber OSM/GTFS/Comuline |

## Non-functional requirements

- Render awal (peta + garis) tidak diblokir oleh chunk 3D — deck.gl/luma.gl
  di-dynamic-import agar peta dasar tampil cepat (lihat komentar di
  `vite.config.js`).
- Update posisi kendaraan berjalan halus (target ~30 FPS) tanpa jank yang
  terlihat pada jumlah kendaraan aktif normal (puluhan, bukan ribuan).
- Seluruh data yang dirender berasal dari file statis yang bisa dibangun
  ulang sepenuhnya secara offline — tidak ada state server untuk dijaga.

## Out of scope

- Tidak ada pelacakan GPS/live data — lihat Non-goals di PROJECT_BRIEF.md.
- Tidak ada backend/API/database sendiri.
- Tidak ada akun pengguna atau personalisasi.
- Moda selain rel & BRT (angkot, ojek online) tidak termasuk.

## Open questions

- Target hosting/deployment belum ditentukan — resolve sebelum milestone
  "deploy pertama" (lihat `docs/ROADMAP.md`).
- Apakah perlu migrasi ke TypeScript mengikuti default stack OS untuk
  gis-app, atau tetap vanilla JS (lihat `docs/decisions/ADR-001-vanilla-js-over-typescript.md`) — resolve saat proyek butuh kontributor lain.
