import './style.css';
import { initMap } from './map/initMap.js';
import { addLineLayers } from './map/lineLayers.js';
import { addStationLayer } from './map/stationLayer.js';

async function loadJson(url) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`gagal memuat ${url}: ${resp.status}`);
  return resp.json();
}

const map = initMap('map');

map.on('load', async () => {
  const [lines, stations] = await Promise.all([
    loadJson('/data/lines.geojson'),
    loadJson('/data/stations.geojson'),
  ]);
  addLineLayers(map, lines);
  addStationLayer(map, stations);
  console.log(
    `Peta siap — ${lines.features.length} jalur, ${stations.features.length} stasiun`
  );
});
