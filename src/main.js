import './style.css';
import { initMap } from './map/initMap.js';
import { addLineLayers, LINE_LAYER_BASE_FILTERS } from './map/lineLayers.js';
import { addStationLayer } from './map/stationLayer.js';
import { createEngine } from './sim/engine.js';
import { simSeconds, serviceDay, setClock } from './sim/clock.js';
import { CONFIG } from './config.js';
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
  const [linesGeo, segmentsGeo, stationsGeo, linesJson] = await Promise.all([
    loadJson('/data/lines.geojson'),
    loadJson('/data/lines_segments.geojson'),
    loadJson('/data/stations.geojson'),
    loadJson('/data/lines.json'),
  ]);

  const day = serviceDay();
  const timetables = await Promise.all(
    linesJson.lines.map((l) => loadJson(`/data/timetables/${l.id}_${day}.json`))
  );

  addLineLayers(map, segmentsGeo);
  addStationLayer(map, stationsGeo);

  const elevatedAll = segmentsGeo.features.filter(
    (f) => f.properties.level === 1
  );

  const engine = createEngine(linesJson, linesGeo, timetables);
  const clockDisplay = createClockDisplay();
  const infoPanel = createInfoPanel(linesJson);

  // indeks stasiun: nama -> daftar {lineId, code} (untuk info transit antar jalur)
  const stationIndex = {};
  for (const f of stationsGeo.features) {
    const { name, lineId, code } = f.properties;
    (stationIndex[name] ??= []).push({ lineId, code });
  }

  // saring jalur yang ditampilkan (dipakai legenda);
  // lapisan garis punya filter dasar per-ketinggian yang harus dipertahankan
  let visibleLines = new Set(linesJson.lines.map((l) => l.id));
  const filteredLayers = [
    'lines-glow', 'lines-core', 'lines-elevated-shadow', 'lines-tunnel',
    'stations-circle', 'stations-label', 'vehicles-glow', 'vehicles-core',
  ];

  function applyVisibility(visible) {
    visibleLines = visible;
    const inExpr = ['in', ['get', 'lineId'], ['literal', [...visible]]];
    for (const layerId of filteredLayers) {
      if (!map.getLayer(layerId)) continue;
      const base = LINE_LAYER_BASE_FILTERS[layerId];
      map.setFilter(layerId, base ? ['all', base, inExpr] : inExpr);
    }
    if (vehicles.setElevatedPaths) {
      vehicles.setElevatedPaths(
        elevatedAll.filter((f) => visible.has(f.properties.lineId))
      );
    }
  }

  createLegend(linesJson, { onToggle: applyVisibility });

  function showVehicleInfo(v) {
    const info = engine.vehicleInfo(v.id, simSeconds());
    if (info) infoPanel.showVehicle(info);
  }

  // dynamic import: deck.gl (dipakai renderer 3D) jadi chunk terpisah yang
  // hanya diunduh browser kalau benar-benar dipakai, dan tidak menunda
  // render peta + jalur yang sudah tampil lebih dulu di atas
  const vehicles =
    CONFIG.vehicleRenderer === '3d'
      ? await import('./render/vehicles3d.js').then((m) =>
          m.createVehicles3d(map, { onPick: showVehicleInfo })
        )
      : await import('./render/vehicles2d.js').then((m) => m.createVehicles2d(map));
  if (vehicles.setElevatedPaths) vehicles.setElevatedPaths(elevatedAll);

  // klik stasiun -> panel info
  map.on('click', 'stations-circle', (e) => {
    const { name } = e.features[0].properties;
    infoPanel.showStation(name, stationIndex[name] ?? []);
  });

  // klik kereta 2D -> panel info (renderer 3D punya picking sendiri)
  if (CONFIG.vehicleRenderer !== '3d') {
    map.on('click', 'vehicles-core', (e) =>
      showVehicleInfo({ id: e.features[0].properties.id })
    );
  }

  for (const hoverable of ['stations-circle']) {
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

  // posisi kendaraan diperbarui 30x/detik (cukup mulus, hemat GPU);
  // peta sendiri tetap bebas merender 60 fps
  let lastVehicleUpdate = 0;
  function frame(now) {
    if (now - lastVehicleUpdate >= 33) {
      lastVehicleUpdate = now;
      const t = simSeconds();
      const positions = engine.positionsAt(t).filter((v) =>
        visibleLines.has(v.lineId)
      );
      vehicles.update(positions);
      clockDisplay.update(t, positions.length);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  console.log(
    `Peta siap — ${linesGeo.features.length} jalur, ` +
      `${stationsGeo.features.length} stasiun, layanan ${day}`
  );
});
