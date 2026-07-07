// Jam simulasi WIB (UTC+7), tidak bergantung zona waktu PC pengguna.
// Untuk pengujian bisa dipercepat / dilompat dari konsol browser:
//   __clock.set({ mult: 60 })            -> 1 detik nyata = 1 menit simulasi
//   __clock.set({ at: '08:00', mult: 1 }) -> lompat ke jam 08:00

const state = { mult: 1, baseSim: null, baseReal: null };

function hmToSec(hm) {
  const [h, m] = hm.split(':').map(Number);
  return h * 3600 + m * 60;
}

function nowWibSec() {
  const ms = Date.now() + 7 * 3600 * 1000;
  return (ms / 1000) % 86400;
}

export function simSeconds() {
  if (state.baseSim === null) return nowWibSec();
  const elapsed = (Date.now() - state.baseReal) / 1000;
  return (state.baseSim + elapsed * state.mult) % 86400;
}

export function serviceDay() {
  const d = new Date(Date.now() + 7 * 3600 * 1000);
  const dow = d.getUTCDay(); // 0=Minggu .. 6=Sabtu (tanggal WIB)
  return dow === 0 || dow === 6 ? 'weekend' : 'weekday';
}

export function setClock({ mult = 1, at = null } = {}) {
  state.baseSim = at === null ? simSeconds() : hmToSec(at);
  state.baseReal = Date.now();
  state.mult = mult;
}

export function formatSim(t) {
  const s = Math.floor(t) % 86400;
  const hh = String(Math.floor(s / 3600)).padStart(2, '0');
  const mm = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
  const ss = String(s % 60).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}
