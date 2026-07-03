// Titik stasiun: lingkaran putih kecil + label nama saat zoom dekat.

export function addStationLayer(map, stationsGeojson) {
  map.addSource('stations', { type: 'geojson', data: stationsGeojson });

  map.addLayer({
    id: 'stations-circle',
    type: 'circle',
    source: 'stations',
    minzoom: 10,
    paint: {
      'circle-color': '#ffffff',
      'circle-radius': [
        'interpolate', ['linear'], ['zoom'],
        10, 1.5,
        13, 3.5,
        16, 6,
      ],
      'circle-stroke-color': ['get', 'color'],
      'circle-stroke-width': [
        'interpolate', ['linear'], ['zoom'],
        10, 0.5,
        13, 1.5,
        16, 2.5,
      ],
    },
  });

  map.addLayer({
    id: 'stations-label',
    type: 'symbol',
    source: 'stations',
    minzoom: 12,
    layout: {
      'text-field': ['get', 'name'],
      'text-size': 11,
      'text-offset': [0, 1.1],
      'text-anchor': 'top',
      'text-font': ['Open Sans Regular'],
    },
    paint: {
      'text-color': '#d8d8e0',
      'text-halo-color': '#0b0b12',
      'text-halo-width': 1.2,
    },
  });
}
