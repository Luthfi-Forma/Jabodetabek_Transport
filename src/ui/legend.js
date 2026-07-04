// Panel legenda: daftar jalur dengan chip warna + centang tampil/sembunyi,
// dan tombol pengalih bahasa ID/EN.

import { t, getLang, toggleLang, onLangChange } from './i18n.js';

export function createLegend(linesJson, { onToggle }) {
  const visible = new Set(linesJson.lines.map((l) => l.id));
  let collapsed = false;

  const panel = document.createElement('div');
  panel.className = 'legend';
  document.body.appendChild(panel);

  function render() {
    const lang = getLang();
    panel.innerHTML = '';

    const head = document.createElement('div');
    head.className = 'legend-head';
    const title = document.createElement('span');
    title.className = 'legend-title';
    title.textContent = `${collapsed ? '▸' : '▾'} ${t('legendTitle')}`;
    title.addEventListener('click', () => {
      collapsed = !collapsed;
      render();
    });
    const langBtn = document.createElement('button');
    langBtn.className = 'lang-btn';
    langBtn.textContent = t('langButton');
    langBtn.addEventListener('click', toggleLang);
    head.append(title, langBtn);
    panel.appendChild(head);
    if (collapsed) return;

    for (const line of linesJson.lines) {
      const row = document.createElement('label');
      row.className = 'legend-row';

      const box = document.createElement('input');
      box.type = 'checkbox';
      box.checked = visible.has(line.id);
      box.addEventListener('change', () => {
        if (box.checked) visible.add(line.id);
        else visible.delete(line.id);
        onToggle(visible);
      });

      const chip = document.createElement('span');
      chip.className = 'legend-chip';
      chip.style.background = line.color;

      const name = document.createElement('span');
      name.className = 'legend-name';
      name.textContent = line.name[lang];

      row.append(box, chip, name);
      panel.appendChild(row);
    }
  }

  render();
  onLangChange(render);
  return { visible };
}
