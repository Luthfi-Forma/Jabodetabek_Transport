# Testing

## Cara jalanin

Belum ada tes otomatis. Verifikasinya masih manual seluruhnya:

```
npm run dev
```

Terus periksa langsung di browser — lihat daftar di bawah.

## Yang diperiksa

| Lapis | Alat | Cakupannya |
|---|---|---|
| unit | — | belum ada |
| integrasi | — | belum ada |
| manual / e2e | browser + konsol | peta ke-render, semua 10 lin tampil, klik stasiun/kendaraan nampilin info yang benar, `__clock.set()` mengubah simulasi sesuai harapan, dan kendaraan nggak lompat di kasus lintas tengah malam |

Pemeriksaan manual dijalanin tiap kali `src/sim/`, `src/map/`, atau
`src/render/` diubah.

## Data buat tes

Pakai jadwal dan geometri asli yang udah ada di `public/data/`, bukan data
karangan. Semuanya berbasis koordinat dan jadwal Jabodetabek yang sebenarnya.

## Yang belum ketutup

- `src/sim/engine.js` belum ada tes unit — khususnya interpolasi posisi dan
  kasus lintas tengah malam. Ini kandidat pertama kalau nanti nambah tes.
- Skrip `tools/*.py` belum ada tesnya sama sekali, misalnya buat mastiin
  `build_geojson.py` ngasilin path yang benar dari graph OSM.
