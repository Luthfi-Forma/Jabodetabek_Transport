# User Stories — Jabodetabek Transport

- Source: [PRD.md](PRD.md)

<!-- Semua story berstatus "done" karena mendokumentasikan v1 yang sudah
     dibangun, bukan backlog. -->

| ID | Story | Feature | Priority | Status |
|---|---|---|---|---|
| S-01 | Sebagai penggemar transportasi umum, saya ingin melihat seluruh garis dan stasiun Jabodetabek di peta 3D, sehingga saya bisa memahami topologi jaringan secara visual | F-01 | P1 | done |
| S-02 | Sebagai penggemar transportasi umum, saya ingin melihat kendaraan bergerak sesuai jadwal nyata, sehingga saya bisa merasakan dinamika layanan sepanjang hari | F-02 | P1 | done |
| S-03 | Sebagai pengembang yang menguji simulasi, saya ingin mempercepat atau melompatkan jam simulasi dari konsol, sehingga saya tidak perlu menunggu jam sibuk terjadi secara nyata | F-03 | P1 | done |
| S-04 | Sebagai pengguna, saya ingin mengklik kendaraan atau stasiun untuk melihat detailnya, sehingga saya tahu tujuan kendaraan atau lin apa saja yang singgah di sebuah stasiun | F-04 | P1 | done |
| S-05 | Sebagai pengguna, saya ingin menyembunyikan lin tertentu dari legend, sehingga peta tidak terlalu ramai saat saya hanya tertarik pada satu-dua lin | F-05 | P2 | done |
| S-06 | Sebagai pengguna berbahasa Inggris, saya ingin mengganti bahasa UI, sehingga saya bisa memahami label dan panel info | F-06 | P2 | done |
| S-07 | Sebagai pengembang GIS, saya ingin menjalankan ulang pipeline data dengan satu perintah, sehingga saya bisa memperbarui geometri/jadwal saat sumber data berubah | F-07 | P1 | done |

## Story notes

- S-02: kasus tepi penting — kendaraan yang jadwalnya melintasi tengah malam
  dicek pada `t` dan `t+24h` sekaligus (lihat `src/sim/engine.js`) agar tidak
  melompat posisi saat pergantian hari layanan (`serviceDay()` di
  `src/sim/clock.js` membedakan weekday/weekend berdasarkan tanggal WIB).
- S-03: sintaks konsol yang didukung: `__clock.set({ mult: 60 })` (percepat
  60x) dan `__clock.set({ at: '08:00', mult: 1 })` (lompat ke jam 08:00).
