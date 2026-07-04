// Gambar geometri jalur per segmen ketinggian di atas basemap gelap:
// - permukaan  : garis penuh
// - layang     : bayangan tipis di tanah (garis 3D-nya digambar deck.gl)
// - bawah tanah: garis putus-putus redup

export function addLineLayers(map, segmentsGeojson) {
  map.addSource('lines', { type: 'geojson', data: segmentsGeojson });

  // lapisan "glow" untuk jalur permukaan
  map.addLayer({
    id: 'lines-glow',
    type: 'line',
    source: 'lines',
    filter: ['==', ['get', 'level'], 0],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'color'],
      'line-opacity': 0.25,
      'line-width': [
        'interpolate', ['linear'], ['zoom'],
        9, 4,
        13, 10,
        16, 18,
      ],
    },
  });

  map.addLayer({
    id: 'lines-core',
    type: 'line',
    source: 'lines',
    filter: ['==', ['get', 'level'], 0],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'color'],
      'line-opacity': 0.9,
      'line-width': [
        'interpolate', ['linear'], ['zoom'],
        9, 1.5,
        13, 3,
        16, 6,
      ],
    },
  });

  // bayangan jalur layang di permukaan tanah
  map.addLayer({
    id: 'lines-elevated-shadow',
    type: 'line',
    source: 'lines',
    filter: ['==', ['get', 'level'], 1],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': ['get', 'color'],
      'line-opacity': 0.2,
      'line-width': [
        'interpolate', ['linear'], ['zoom'],
        9, 1.5,
        13, 3,
        16, 6,
      ],
    },
  });

  // jalur bawah tanah: putus-putus dan redup
  map.addLayer({
    id: 'lines-tunnel',
    type: 'line',
    source: 'lines',
    filter: ['==', ['get', 'level'], -1],
    paint: {
      'line-color': ['get', 'color'],
      'line-opacity': 0.5,
      'line-dasharray': [2, 2],
      'line-width': [
        'interpolate', ['linear'], ['zoom'],
        9, 1.5,
        13, 3,
        16, 5,
      ],
    },
  });
}

// filter dasar per lapisan (dipertahankan saat legenda menyaring jalur)
export const LINE_LAYER_BASE_FILTERS = {
  'lines-glow': ['==', ['get', 'level'], 0],
  'lines-core': ['==', ['get', 'level'], 0],
  'lines-elevated-shadow': ['==', ['get', 'level'], 1],
  'lines-tunnel': ['==', ['get', 'level'], -1],
};
