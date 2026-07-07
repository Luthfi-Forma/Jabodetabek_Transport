// Renderer kendaraan 3D (deck.gl di atas MapLibre):
// balok memanjang searah rel + lingkaran "glow" di bawahnya.
// Kendaraan mengikuti ketinggian jalur (layang/permukaan/bawah tanah);
// yang di bawah tanah digambar lebih redup. Jalur layang ikut digambar
// sebagai garis 3D melayang (PathLayer) di sini juga.

import { MapboxOverlay } from '@deck.gl/mapbox';
import { SimpleMeshLayer } from '@deck.gl/mesh-layers';
import { ScatterplotLayer, PathLayer } from '@deck.gl/layers';
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
  // interleaved:false = deck menggambar di kanvas sendiri di atas peta.
  // Jauh lebih ringan di GPU terintegrasi daripada mode interleaved
  // (yang menyinkronkan state GL dengan MapLibre setiap frame).
  const overlay = new MapboxOverlay({ interleaved: false, layers: [] });
  map.addControl(overlay);
  const mesh = new CubeGeometry();

  // garis jalur layang (statis; diganti hanya saat filter jalur berubah)
  let elevatedFeatures = [];

  function setElevatedPaths(features) {
    elevatedFeatures = features;
  }

  function update(vehicles) {
    // ukuran dasar dalam meter; diperbesar saat zoom jauh agar tetap terlihat
    const zoom = map.getZoom();
    const sizeScale = 18 * Math.pow(2, Math.max(0, 13.5 - zoom));

    overlay.setProps({
      layers: [
        new PathLayer({
          id: 'elevated-paths',
          data: elevatedFeatures,
          getPath: (f) => f.geometry.coordinates,
          getColor: (f) => hexToRgb(f.properties.color, 200),
          getWidth: 5,
          widthUnits: 'meters',
          widthMinPixels: 1.5,
          jointRounded: true,
          capRounded: true,
          pickable: false,
        }),
        new ScatterplotLayer({
          id: 'vehicles-3d-glow',
          data: vehicles,
          getPosition: (d) => [d.lngLat[0], d.lngLat[1], Math.max(d.alt, 0)],
          getFillColor: (d) => hexToRgb(d.color, d.alt < 0 ? 35 : 70),
          getRadius: sizeScale * 3.5,
          radiusUnits: 'meters',
          radiusMaxPixels: 12,
          pickable: false,
        }),
        new SimpleMeshLayer({
          id: 'vehicles-3d-mesh',
          data: vehicles,
          mesh,
          sizeScale,
          // kendaraan menempel di ketinggian jalurnya; bawah tanah = negatif
          getPosition: (d) => [d.lngLat[0], d.lngLat[1], d.alt + 5],
          getColor: (d) => hexToRgb(d.color, d.alt < 0 ? 140 : 255),
          // bearing = derajat searah jarum jam dari utara;
          // sumbu panjang balok (x) diputar mengikuti arah rel
          getOrientation: (d) => [0, 90 - d.bearing, 0],
          // bus BRT lebih kecil daripada rangkaian kereta
          getScale: (d) =>
            d.mode === 'brt' ? [1.1, 0.55, 0.55] : [2.6, 0.9, 0.9],
          pickable: true,
          onClick: (info) => {
            if (info.object) onPick(info.object);
            return true;
          },
        }),
      ],
    });
  }

  return { update, setElevatedPaths };
}
