# ADR-001: Vanilla JS over TypeScript

Status: Accepted
Date: 2026-07-07

<!-- ADR ini mendokumentasikan keputusan yang sudah berlaku sejak proyek ini
     dibangun (sebelum diretrofit ke bawah Claude Engineering OS), bukan
     keputusan baru — statusnya langsung Accepted, bukan Proposed. -->

## Context

Claude Engineering OS menetapkan TypeScript sebagai bahasa frontend default
untuk proyek bertipe `gis-app` (`standards/coding/typescript.md`,
`templates/project-types/gis-app/manifest.json`). Proyek ini, bagaimanapun,
sudah dibangun sepenuhnya dengan JavaScript ES modules biasa (`src/**/*.js`,
tanpa `tsconfig.json`, tanpa dependensi `typescript`) sebelum diadopsi ke
struktur OS. Dokumentasi harus mencerminkan realita kode, bukan
menyembunyikan penyimpangan dari default.

## Decision

1. Proyek ini tetap menggunakan JavaScript ES modules biasa (bukan
   TypeScript) untuk seluruh kode `src/`.
2. Penyimpangan ini dicatat di `docs/RULES.md` sebagai deviasi resmi dari
   standar OS, dengan rujukan ke ADR ini.
3. Migrasi ke TypeScript tetap terbuka sebagai item Icebox
   (`docs/ROADMAP.md`) bila proyek butuh kontributor tambahan atau tipe data
   yang lebih kompleks.

## Rationale

- Proyek ini adalah visualisasi satu-orang dengan permukaan kode yang relatif
  kecil (< 15 modul di `src/`); overhead penyiapan TypeScript (tsconfig,
  build step tambahan, anotasi tipe untuk API MapLibre/deck.gl yang sudah
  menyediakan `.d.ts` sendiri) tidak sepadan dengan manfaatnya pada skala
  ini.
- Menulis ulang kode yang sudah berjalan (`src/map/`, `src/render/`,
  `src/sim/`, `src/ui/`) ke TypeScript murni untuk kepatuhan dokumentasi
  berisiko memperkenalkan regresi tanpa menambah nilai fungsional.
- MapLibre GL dan deck.gl sudah menyediakan tipe TypeScript sendiri secara
  opsional — migrasi di masa depan tetap memungkinkan tanpa mengubah
  dependensi runtime.

## Alternatives considered

- **Migrasi penuh ke TypeScript sekarang** — ditolak: biaya migrasi (rewrite
  + verifikasi ulang seluruh modul) tidak proporsional dengan ukuran proyek
  saat ini; tidak ada bug kelas "salah tipe" yang pernah terjadi yang akan
  dicegah olehnya.
- **Migrasi bertahap (JSDoc + `checkJs`)** — dipertimbangkan sebagai jalan
  tengah, tapi belum diputuskan; dicatat sebagai kemungkinan follow-up bila
  kebutuhan tipe muncul (mis. saat menambah kontributor baru).
- **Tidak melakukan apa-apa (biarkan tanpa ADR)** — ditolak: standar OS
  mewajibkan deviasi tooling struktural dicatat sebagai ADR
  (`templates/docs/RULES.md`), agar sesi Claude Code berikutnya tidak
  mengira ini adalah kelalaian yang belum disadari.

## Consequences

- Lebih mudah: kontribusi cepat tanpa build step tambahan; konsisten dengan
  kode yang sudah ada.
- Lebih sulit: tidak ada pengecekan tipe statis untuk mencegah kesalahan
  seperti argumen salah urutan ke fungsi `sim/engine.js` atau `render/*.js`
  — mitigasi saat ini adalah tinjauan manual dan (di masa depan) test unit
  per `docs/ROADMAP.md` M3.
- Follow-up: bila migrasi ke TypeScript pernah dilakukan, ADR ini harus
  di-supersede oleh ADR baru, bukan diedit.
