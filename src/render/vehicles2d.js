// Renderer kendaraan 2D: lingkaran menyala yang bergerak di sepanjang jalur.
// Sederhana dan cepat — juga berguna sebagai renderer debug saat versi 3D ada.

export function createVehicles2d(map) {
  map.addSource('vehicles', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
  });

  map.addLayer({
    id: 'vehicles-glow',
    type: 'circle',
    source: 'vehicles',
    paint: {
      'circle-color': ['get', 'color'],
      'circle-opacity': 0.35,
      'circle-blur': 1,
      'circle-radius': [
        'interpolate', ['linear'], ['zoom'],
        9, 5,
        13, 10,
        16, 16,
      ],
    },
  });

  map.addLayer({
    id: 'vehicles-core',
    type: 'circle',
    source: 'vehicles',
    paint: {
      'circle-color': ['get', 'color'],
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 1,
      'circle-radius': [
        'interpolate', ['linear'], ['zoom'],
        9, 2.5,
        13, 5,
        16, 8,
      ],
    },
  });

  function update(vehicles) {
    map.getSource('vehicles').setData({
      type: 'FeatureCollection',
      features: vehicles.map((v) => ({
        type: 'Feature',
        properties: {
          id: v.id,
          lineId: v.lineId,
          color: v.color,
          dest: v.dest,
        },
        geometry: { type: 'Point', coordinates: v.lngLat },
      })),
    });
  }

  return { update };
}
