import './style.css';
import { initMap } from './map/initMap.js';

const map = initMap('map');

map.on('load', () => {
  console.log('Peta siap — Jakarta dark map loaded');
});
