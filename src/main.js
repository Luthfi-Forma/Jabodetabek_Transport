import './style.css';
import { initMap } from './map/initMap.js';
import { addLineLayers } from './map/lineLayers.js';
import { addStationLayer } from './map/stationLayer.js';
import { createEngine } from './sim/engine.js';
import { simSeconds, serviceDay, setClock } from './sim/clock.js';
import { createVehicles2d } from './render/vehicles2d.js';
import { createClockDisplay } from './ui/clockDisplay.js';
import { createLegend } from './ui/legend.js';
import { createInfoPanel } from './ui/infoPanel.js';

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
  const clockDisplay = createClockDisplay();
  const infoPanel = createInfoPanel(linesJson);

  // indeks stasiun: nama -> daftar {lineId, code} (untuk info transit antar jalur)
  const stationIndex = {};
  for (const f of stationsGeo.features) {
    const { name, lineId, code } = f.properties;
    (stationIndex[name] ??= []).push({ lineId, code });
  }

  // saring jalur yang ditampilkan (dipakai legenda)
  let visibleLines = new Set(linesJson.lines.map((l) => l.id));
  const filteredLayers = [
    'lines-glow', 'lines-core', 'stations-circle', 'stations-label',
    'vehicles-glow', 'vehicles-core',
  ];

  function applyVisibility(visible) {
    visibleLines = visible;
    const filter = ['in', ['get', 'lineId'], ['literal', [...visible]]];
    for (const layerId of filteredLayers) {
      if (map.getLayer(layerId)) map.setFilter(layerId, filter);
    }
  }

  createLegend(linesJson, { onToggle: applyVisibility });

  const vehicles = createVehicles2d(map);

  // klik stasiun -> panel info
  map.on('click', 'stations-circle', (e) => {
    const { name } = e.features[0].properties;
    infoPanel.showStation(name, stationIndex[name] ?? []);
  });

  // klik kereta -> panel info
  map.on('click', 'vehicles-core', (e) => {
    const info = engine.vehicleInfo(e.features[0].properties.id, simSeconds());
    if (info) infoPanel.showVehicle(info);
  });

  for (const hoverable of ['stations-circle', 'vehicles-core']) {
    map.on('mouseenter', hoverable, () => {
      map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', hoverable, () => {
      map.getCanvas().style.cursor = '';
    });
  }

  // alat uji dari konsol browser: __clock.set({ mult: 60, at: '07:30' })
  window.__clock = { set: setClock };
  window.__map = map;
  window.__engine = engine;

  function frame() {
    const t = simSeconds();
    const positions = engine.positionsAt(t).filter((v) =>
      visibleLines.has(v.lineId)
    );
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
