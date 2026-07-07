# Project Brief — Jabodetabek Transport

> Peta 3D interaktif transportasi umum Jabodetabek (KRL, MRT, LRT, TransJakarta) dengan simulasi posisi kendaraan real-time berbasis jadwal, dibangun dengan Vite + MapLibre GL + deck.gl.

- Date: 2026-07-07
- Status: Approved
<!-- Brief ini bersifat deskriptif: mendokumentasikan sistem yang sudah dibangun,
     bukan proposal untuk sesuatu yang belum ada. -->

## Problem

Jaringan transportasi umum Jabodetabek terdiri dari banyak operator dan moda
yang berbeda (KRL Commuter Line, MRT Jakarta, LRT Jakarta, LRT Jabodebek,
TransJakarta BRT) tanpa satu visualisasi terpadu yang menunjukkan bagaimana
kendaraan-kendaraan ini benar-benar bergerak sepanjang hari berdasarkan
jadwal resminya. Peta integrasi resmi (mis. Peta Integrasi FDTJ) bersifat
statis — bagus untuk melihat topologi jaringan, tapi tidak menunjukkan
dinamika layanan (headway, jam sibuk, posisi kendaraan per waktu).

## Audience

- Penggemar transportasi umum dan pemerhati kota (railfan/transit enthusiast)
  yang ingin melihat visualisasi jaringan Jabodetabek secara hidup.
- Pengembang lain yang ingin mereplikasi pola integrasi data multi-sumber
  (OSM + GTFS + jadwal operator) untuk kota/jaringan transit lain.

## Proposed solution

Aplikasi web satu halaman yang merender peta 3D gelap (MapLibre GL) berisi
seluruh garis dan stasiun/halte Jabodetabek, dengan kendaraan (balok 3D via
deck.gl) yang bergerak sepanjang rute mengikuti jadwal nyata/sintetis per
lin. Jam simulasi berjalan mengikuti WIB dan bisa dipercepat/dilompat dari
konsol untuk pengujian. Data geometri dan jadwal dihasilkan lebih dulu secara
offline oleh pipeline Python (`tools/`) dari sumber OSM, GTFS TransJakarta,
dan API komunitas KRL, lalu disajikan sebagai file JSON/GeoJSON statis —
tidak ada backend atau database di produksi.

## Scope (v1)

- Render seluruh 10 lin: KRL (A, B, C, R, T, TP), MRT (M), LRT Jakarta (S),
  LRT Jabodebek (CB, BK), TransJakarta BRT (TJ1–TJ14).
- Layer garis dengan kesadaran elevasi (layang = glow, permukaan = solid,
  bawah tanah = putus-putus) dan layer stasiun yang bisa diklik.
- Simulasi kendaraan berjalan di sepanjang rute berdasarkan jadwal
  weekday/weekend per lin, dengan easing kubik antar-stasiun.
- Panel info saat stasiun/kendaraan diklik (lin yang melayani, tujuan,
  stasiun berikutnya).
- Legend yang bisa dilipat dengan toggle tampil/sembunyi per lin.
- UI dwibahasa (Indonesia/Inggris).
- Pipeline data offline yang bisa dijalankan ulang (`tools/refresh_all.py`)
  untuk memperbarui geometri dan jadwal.

## Non-goals

- Tidak ada pelacakan GPS langsung/real-time dari operator — posisi
  kendaraan adalah simulasi berbasis jadwal, bukan data live.
- Tidak ada backend/API sendiri atau database — semua data adalah file
  statis yang dibangun offline.
- Tidak ada akun pengguna, autentikasi, atau personalisasi.
- Tidak menargetkan moda selain rel & BRT (mis. angkot, ojek online) di v1.
- Belum ada strategi deployment/hosting resmi (lihat `docs/ROADMAP.md`).

## Success criteria

- Pengguna dapat melihat seluruh 10 lin tampil benar di peta tanpa error
  render.
- Kendaraan bergerak mulus mengikuti jadwal, termasuk kasus lintas tengah
  malam.
- Klik stasiun/kendaraan menampilkan info yang akurat dan relevan.
- `npm run dev` berjalan dan menampilkan peta dalam < 5 langkah dari clone
  (lihat `docs/DEVELOPMENT.md`).
- Pipeline `tools/refresh_all.py` dapat menghasilkan ulang seluruh data di
  `public/data/` tanpa intervensi manual.

## Constraints

- Basemap gratis tanpa token (CartoDB Dark Matter) — tidak ada anggaran
  layanan peta berbayar.
- Data KRL bergantung pada API pihak ketiga (comuline.com), bukan API resmi
  KAI Commuter — berisiko berubah/down sewaktu-waktu.
- Data TransJakarta bergantung pada feed GTFS resmi mereka
  (gtfs.transjakarta.co.id) — format/ketersediaan bisa berubah.
- Kurasi urutan stasiun manual berpatokan pada Peta Integrasi FDTJ 2026-06
  (`2026-06a-Peta-Integrasi-Jakarta-FDTJ-Web.pdf`), perlu di-refresh manual
  bila peta resmi berubah.

## References

- `2026-06a-Peta-Integrasi-Jakarta-FDTJ-Web.pdf` — Peta Integrasi Jakarta,
  FDTJ (Forum Duduk Transportasi Jakarta), edisi Juni 2026. Sumber kebenaran
  kurasi lin/stasiun di `data/curated/lines_meta.json`.
- OpenStreetMap Overpass API — geometri rute & lokasi stasiun mentah.
- TransJakarta GTFS feed (https://gtfs.transjakarta.co.id) — korridor,
  halte, dan dwell time BRT.
- Comuline API (https://api.comuline.com) — cermin jadwal KRL Commuter Line.
- Referensi visual/gaya: mini-tokyo-3d (lihat `package.json` name:
  `mini-jakarta-3d`).
