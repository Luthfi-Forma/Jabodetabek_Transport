# Project Rules — Jabodetabek Transport

- Updated: 2026-07-07

This project follows Claude Engineering OS standards by default (see
`CLAUDE.md`, "Standards in force"). **This file records only the deltas** —
where this project deliberately deviates from an OS standard, and why.

## Deviations from OS standards

| OS rule (file + rule) | This project does | Why / ADR |
|---|---|---|
| `standards/coding/typescript.md` — TS as default frontend language for gis-app | Vanilla JavaScript ES modules, no TypeScript, no build-time type checking | [ADR-001](decisions/ADR-001-vanilla-js-over-typescript.md) |

## Project-specific conventions

- Komentar kode dan string UI ditulis dalam Bahasa Indonesia (bahasa asli
  proyek ini sejak awal, mendahului kebijakan bahasa OS).
- Jam simulasi selalu dalam WIB (UTC+7), independen dari zona waktu OS
  pengguna — lihat `src/sim/clock.js`.
- Kode stasiun/lin mengikuti format `{kodeLin}-{nomorUrut}` (mis. `M-01`,
  `CB-09`), didefinisikan manual di `data/curated/lines_meta.json` dan wajib
  searah dengan relation OSM yang dirujuk di `tools/osm_relations.json`
  (lihat komentar `"comment"` di awal `lines_meta.json`).
- Skrip di `tools/` hanya memakai Python stdlib (tidak ada
  `requirements.txt`) — pertahankan ini kecuali ada kebutuhan kuat untuk
  dependensi pihak ketiga.
