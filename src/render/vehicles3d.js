// Renderer kendaraan 3D (deck.gl di atas MapLibre):
// balok memanjang searah rel + lingkaran "glow" di bawahnya.
// Bisa diklik (picking) untuk menampilkan info kereta.

import { MapboxOverlay } from '@deck.gl/mapbox';
import { SimpleMeshLayer } from '@deck.gl/mesh-layers';
import { ScatterplotLayer } from '@deck.gl/layers';
import { CubeGeometry } from '@luma.gl/engine';

function hexToRgb(hex, alpha = 255) {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
    alpha,
  ];
}

export function createVehicles3d(map, { onPick }) {
  const overlay = new MapboxOverlay({ interleaved: true, layers: [] });
  map.addControl(overlay);
  const mesh = new CubeGeometry();

  function update(vehicles) {
    // ukuran dasar dalam meter; diperbesar saat zoom jauh agar tetap terlihat
    const zoom = map.getZoom();
    const sizeScale = 18 * Math.pow(2, Math.max(0, 13.5 - zoom));

    overlay.setProps({
      layers: [
        new ScatterplotLayer({
          id: 'vehicles-3d-glow',
          data: vehicles,
          getPosition: (d) => d.lngLat,
          getFillColor: (d) => hexToRgb(d.color, 70),
          getRadius: sizeScale * 3.5,
          radiusUnits: 'meters',
          pickable: false,
        }),
        new SimpleMeshLayer({
          id: 'vehicles-3d-mesh',
          data: vehicles,
          mesh,
          sizeScale,
          getPosition: (d) => [d.lngLat[0], d.lngLat[1], 6],
          getColor: (d) => hexToRgb(d.color),
          // bearing = derajat searah jarum jam dari utara;
          // sumbu panjang balok (x) diputar mengikuti arah rel
          getOrientation: (d) => [0, 90 - d.bearing, 0],
          getScale: [2.6, 0.9, 0.9],
          pickable: true,
          onClick: (info) => {
            if (info.object) onPick(info.object);
            return true;
          },
        }),
      ],
    });
  }

  return { update };
}
