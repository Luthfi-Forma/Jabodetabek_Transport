# ADR-001: Vanilla JS, bukan TypeScript

Status: Accepted
Date: 2026-07-07

Catatan: ADR ini merekam keputusan yang udah berlaku sejak proyeknya dibangun,
bukan keputusan baru. Makanya statusnya langsung Accepted.

## Ceritanya

Buat proyek peta kayak gini, TypeScript itu pilihan default yang wajar. Tapi
proyek ini terlanjur dibangun sepenuhnya pakai JavaScript ES modules biasa —
`src/**/*.js`, tanpa `tsconfig.json`, tanpa dependensi `typescript`.

Daripada dokumentasinya pura-pura ngikutin default, mending nyatet apa
adanya.

## Keputusannya

1. Kode di `src/` tetap pakai JavaScript ES modules biasa, bukan TypeScript.
2. Pindah ke TypeScript tetap terbuka kalau nanti proyeknya nambah
   kontributor atau tipe datanya makin ribet.

## Kenapa

- Ini visualisasi yang dikerjain sendirian dengan permukaan kode yang kecil —
  kurang dari 15 modul di `src/`. Ongkos nyiapin TypeScript (tsconfig, build
  step tambahan, anotasi tipe) nggak sepadan di skala segini.
- Nulis ulang kode yang udah jalan (`src/map/`, `src/render/`, `src/sim/`,
  `src/ui/`) ke TypeScript cuma demi kepatuhan itu berisiko bikin regresi
  tanpa nambah nilai apa pun.
- MapLibre GL sama deck.gl udah nyediain tipe TypeScript sendiri. Jadi migrasi
  nanti tetap mungkin tanpa ganti dependensi runtime.

## Yang sempat dipertimbangin

- **Migrasi penuh ke TypeScript sekarang** — ditolak. Ongkos rewrite dan
  verifikasi ulang seluruh modul nggak sebanding sama ukuran proyeknya. Lagipula
  belum pernah ada bug kelas "salah tipe" yang bakal kecegah sama ini.
- **Migrasi bertahap pakai JSDoc + `checkJs`** — masih dipertimbangin sebagai
  jalan tengah, belum diputusin. Dicatat sebagai kemungkinan lanjutan kalau
  kebutuhan tipe muncul.

## Konsekuensinya

- Jadi gampang: kontribusi cepat tanpa build step tambahan, dan konsisten sama
  kode yang udah ada.
- Jadi susah: nggak ada pengecekan tipe statis yang bisa nangkep kesalahan
  kayak argumen kebalik pas manggil fungsi di `sim/engine.js` atau
  `render/*.js`. Sementara ini diakalin pakai tinjauan manual.
- Kalau nanti beneran migrasi ke TypeScript, ADR ini di-supersede sama ADR
  baru — jangan diedit di tempat.
