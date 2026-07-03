import './style.css';
import { initMap } from './map/initMap.js';
import { addLineLayers } from './map/lineLayers.js';
import { addStationLayer } from './map/stationLayer.js';
import { createEngine } from './sim/engine.js';
import { simSeconds, serviceDay, setClock } from './sim/clock.js';
import { createVehicles2d } from './render/vehicles2d.js';
import { createClockDisplay } from './ui/clockDisplay.js';

async function loadJson(url) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`gagal memuat ${url}: ${resp.status}`);
  return resp.json();
}

const map = initMap('map');

map.on('load', async () => {
  const [linesGeo, stationsGeo, linesJson] = await Promise.all([
    loadJson('/data/lines.geojson'),
    loadJson('/data/stations.geojson'),
    loadJson('/data/lines.json'),
  ]);

  const day = serviceDay();
  const timetables = await Promise.all(
    linesJson.lines.map((l) => loadJson(`/data/timetables/${l.id}_${day}.json`))
  );

  addLineLayers(map, linesGeo);
  addStationLayer(map, stationsGeo);

  const engine = createEngine(linesJson, linesGeo, timetables);
  const vehicles = createVehicles2d(map);
  const clockDisplay = createClockDisplay();

  // alat uji dari konsol browser: __clock.set({ mult: 60, at: '07:30' })
  window.__clock = { set: setClock };
  window.__map = map;
  window.__engine = engine;

  function frame() {
    const t = simSeconds();
    const positions = engine.positionsAt(t);
    vehicles.update(positions);
    clockDisplay.update(t, positions.length);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  console.log(
    `Peta siap — ${linesGeo.features.length} jalur, ` +
      `${stationsGeo.features.length} stasiun, layanan ${day}`
  );
});
