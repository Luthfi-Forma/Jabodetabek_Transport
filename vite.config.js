import { defineConfig } from 'vite';

// Pisahkan library besar jadi chunk sendiri:
// - maplibre-gl selalu dibutuhkan (peta dasar), tapi tetap dipisah supaya
//   browser bisa cache-nya terpisah dari kode aplikasi yang lebih sering berubah.
// - deck.gl/luma.gl hanya dipakai renderer 3D, yang di-dynamic-import di
//   main.js -- jadi otomatis jadi chunk async terpisah dan tidak
//   menghalangi render peta+jalur pertama kali.
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined;
          if (id.includes('maplibre-gl')) return 'vendor-maplibre';
          if (
            id.includes('deck.gl') ||
            id.includes('@luma.gl') ||
            id.includes('@math.gl') ||
            id.includes('@loaders.gl')
          ) {
            return 'vendor-deck';
          }
          return 'vendor';
        },
      },
    },
  },
});
