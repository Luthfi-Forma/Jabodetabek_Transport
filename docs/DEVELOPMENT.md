# Cara Ngoprek

## Siapin sekali di awal

1. Install Node.js (buat Vite) dan Python 3.8+ (buat pipeline data di
   `tools/` — cuma pakai stdlib, nggak ada `requirements.txt`).
2. Clone repo, terus di root proyek:

   ```
   npm install
   ```

3. (Opsional) Bangun ulang data dari sumbernya — lihat "Refresh data" di
   bawah. Data hasil build udah ada di `public/data/`, jadi ini nggak wajib
   kalau cuma mau jalanin aplikasinya.

## Jalanin

```
npm run dev
```

Buka `http://localhost:5173`.

## Kerjaan yang sering diulang

### Refresh data rutin (jadwal & BRT)

```
python tools/refresh_all.py
```

Ngunduh ulang jadwal KRL dari comuline, feed GTFS TransJakarta, terus bangun
ulang jadwal headway sama koridor BRT.

### Refresh data penuh (termasuk geometri rel)

```
python tools/refresh_all.py --full
```

Ikut ngunduh ulang geometri rel dari OpenStreetMap Overpass sebelum langkah
rutin di atas. Cuma perlu dijalanin kalau ada perubahan rute atau stasiun di
lapangan.

**Urutannya penting.** Langkah geometri (`build_geojson.py`) nimpa
`lines.json` dari nol, sedangkan langkah BRT (`build_brt.py`) nggabungin data
BRT ke file yang sama. Jadi jangan jalanin `build_brt.py` sebelum
`build_geojson.py` kalau pakai `--full`. `refresh_all.py` udah jagain urutan
ini otomatis.

### Build produksi

```
npm run build
```

Hasilnya di `dist/`, situs statis murni.

### Tes

Belum ada tes otomatis. Verifikasinya masih manual — lihat
[TESTING.md](TESTING.md).

## Kalau mentok

| Gejala | Penyebabnya | Bebersihnya |
|---|---|---|
| Render 3D kendaraan lemot atau patah-patah pas pertama load | deck.gl/luma.gl sengaja di-dynamic-import biar nggak ngeblok render peta dasar; chunk `vendor-deck` baru dimuat setelah petanya tampil | Normal, tunggu beberapa ratus milidetik. Kalau mau cek render 2D duluan, set `vehicleRenderer: '2d'` di `src/config.js` |
| Jadwal KRL/GTFS gagal diunduh pas `refresh_all.py` | Sumber pihak ketiga (comuline.com) atau feed resmi TransJakarta lagi down atau ganti format | Cek koneksi sama URL di `tools/fetch_krl_comuline.py` / `tools/fetch_gtfs.py`. Data lama di `public/data/` tetap jalan sampai refresh-nya berhasil |
| Kendaraan "lompat" di sekitar tengah malam | Jadwal yang lewat tengah malam butuh pengecekan `t` dan `t+24h` sekaligus | Pastiin logika di `src/sim/engine.js` nggak diubah tanpa mempertahankan pengecekan dua waktu itu |
