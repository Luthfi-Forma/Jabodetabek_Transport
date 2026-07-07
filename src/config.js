export const CONFIG = {
  // Basemap gelap gratis tanpa token. Cadangan: https://tiles.openfreemap.org/styles/dark
  basemapStyle: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
  center: [106.83, -6.21], // pusat Jakarta
  zoom: 11,
  pitch: 60,
  bearing: 0,

  // '3d' = balok deck.gl (utama), '2d' = lingkaran MapLibre (debug/cadangan)
  vehicleRenderer: '3d',
};
