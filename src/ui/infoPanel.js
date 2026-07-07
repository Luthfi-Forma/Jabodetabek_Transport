// Panel info di kiri-bawah: detail stasiun atau kereta yang diklik.

import { t, getLang, onLangChange } from './i18n.js';

export function createInfoPanel(linesJson) {
  const lineById = Object.fromEntries(linesJson.lines.map((l) => [l.id, l]));

  const panel = document.createElement('div');
  panel.className = 'info-panel hidden';
  document.body.appendChild(panel);

  let current = null; // {type:'station'|'vehicle', ...} untuk render ulang saat ganti bahasa

  function chipHtml(lineId) {
    const line = lineById[lineId];
    if (!line) return '';
    return `<span class="info-chip" style="background:${line.color}"></span>` +
      `<span>${line.name[getLang()]}</span>`;
  }

  function render() {
    if (!current) return;
    if (current.type === 'station') {
      const rows = current.entries
        .map(
          (e) =>
            `<div class="info-row">${chipHtml(e.lineId)}` +
            `<span class="info-code">${e.code}</span></div>`
        )
        .join('');
      panel.innerHTML =
        `<div class="info-title">${current.name}</div>` +
        `<div class="info-sub">${t('station')}</div>${rows}` +
        `<button class="info-close">${t('close')}</button>`;
    } else {
      const next = current.nextStation
        ? `<div class="info-line">${t('nextStation')}: <b>${current.nextStation}</b></div>`
        : `<div class="info-line">${t('arrived')}</div>`;
      panel.innerHTML =
        `<div class="info-row info-title-row">${chipHtml(current.lineId)}</div>` +
        `<div class="info-line">${t('destination')}: <b>${current.dest}</b></div>` +
        next +
        `<button class="info-close">${t('close')}</button>`;
    }
    panel.classList.remove('hidden');
    panel.querySelector('.info-close').addEventListener('click', hide);
  }

  function hide() {
    current = null;
    panel.classList.add('hidden');
  }

  onLangChange(render);

  return {
    showStation(name, entries) {
      current = { type: 'station', name, entries };
      render();
    },
    showVehicle({ lineId, dest, nextStation }) {
      current = { type: 'vehicle', lineId, dest, nextStation };
      render();
    },
    hide,
  };
}
