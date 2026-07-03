import { formatSim } from '../sim/clock.js';

export function createClockDisplay() {
  const el = document.createElement('div');
  el.className = 'sim-clock';
  document.body.appendChild(el);

  return {
    update(t, nVehicles) {
      el.textContent = `${formatSim(t)} WIB · ${nVehicles} kereta`;
    },
  };
}
