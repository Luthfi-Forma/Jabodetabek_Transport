import { formatSim } from '../sim/clock.js';
import { t } from './i18n.js';

export function createClockDisplay() {
  const el = document.createElement('div');
  el.className = 'sim-clock';
  document.body.appendChild(el);

  return {
    update(time, nVehicles) {
      el.textContent = `${formatSim(time)} WIB · ${nVehicles} ${t('trains')}`;
    },
  };
}
