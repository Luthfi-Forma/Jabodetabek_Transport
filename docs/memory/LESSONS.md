# Lessons Learned — Jabodetabek Transport

<!-- APPEND-ONLY, newest first. Write an entry after: a bug with a non-obvious
     cause, a milestone retro, or whenever something cost more than an hour to
     learn. Tag with topics (#python #gis #fastapi ...) so /harvest-lessons can
     classify. Mark entries worth generalizing to the OS with [harvest-candidate];
     after harvesting they get marked [harvested YYYY-MM-DD]. -->

## 2026-07-07 — Integrasi data transit multi-sumber butuh lapisan kurasi manual

Tags: #gis #data-pipeline [harvest-candidate]

Menggabungkan data dari tiga sumber independen (geometri OSM, GTFS resmi
TransJakarta, jadwal komunitas comuline.com untuk KRL) tidak bisa sepenuhnya
otomatis: nama stasiun antar-sumber berbeda, urutan stasiun perlu divalidasi
terhadap peta resmi (`2026-06a-Peta-Integrasi-Jakarta-FDTJ-Web.pdf`), dan
elevasi rute (layang/permukaan/bawah tanah) tidak selalu tersedia di data
mentah. Solusinya: satu file kurasi manual (`data/curated/lines_meta.json`)
sebagai sumber kebenaran urutan stasiun + override nama/koordinat, dipisah
tegas dari data mentah hasil fetch. Pola ini — sumber mentah otomatis + satu
lapis kurasi manual eksplisit yang di-commit ke git — kemungkinan berguna
untuk proyek pemetaan transit lain yang menggabungkan OSM dengan feed
operator resmi.

## 2026-07-07 — Proyek scaffolded

Tags: #meta

Struktur dokumentasi Claude Engineering OS diretrofit ke proyek yang sudah
ada (bukan scaffold baru) karena proyek ini dibangun sebelum diadopsi ke
bawah OS.
