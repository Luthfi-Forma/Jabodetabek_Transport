// Gambar geometri jalur dengan warna masing-masing di atas basemap gelap.

export function addLineLayers(map, linesGeojson) {
  map.addSource('lines', { type: 'geojson', data: linesGeojson });

  // lapisan "glow" lebar dan transparan di bawah garis utama
  map.addLayer({
    id: 'lines-glow',
    type: 'line',
    source: 'lines',
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
}
