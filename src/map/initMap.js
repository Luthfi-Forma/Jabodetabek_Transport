import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { CONFIG } from '../config.js';

export function initMap(containerId) {
  const map = new maplibregl.Map({
    container: containerId,
    style: CONFIG.basemapStyle,
    center: CONFIG.center,
    zoom: CONFIG.zoom,
    pitch: CONFIG.pitch,
    bearing: CONFIG.bearing,
    antialias: true,
  });

  map.addControl(
    new maplibregl.NavigationControl({ visualizePitch: true }),
    'top-right'
  );

  return map;
}
