# Technical Debt — Jabodetabek Transport

<!-- APPEND-ONLY register. Add a row the moment a shortcut is consciously
     taken (CLAUDE.md, Session protocol) — not weeks later from memory.
     Severity: high = risks correctness/security, med = slows work,
     low = cosmetic. Close by filling "Closed by" (commit or ADR), keep the row. -->

| # | Date | Debt item | Severity | Why taken | Cost to fix | Closed by |
|---|---|---|---|---|---|---|
| 1 | 2026-07-07 | Tidak ada test otomatis (unit/integration/e2e) sama sekali | med | Proyek dibangun cepat sebagai visualisasi personal sebelum diadopsi ke bawah Claude Engineering OS; verifikasi dilakukan manual di browser | Siapkan satu lapis test unit untuk `src/sim/engine.js` (interpolasi posisi, kasus lintas tengah malam) sebagai titik awal — lihat `docs/ROADMAP.md` M3 | |
