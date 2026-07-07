// Kamus dua bahasa sederhana. Bahasa Indonesia sebagai bawaan.

import id from '../locales/id.json';
import en from '../locales/en.json';

const dicts = { id, en };
let lang = 'id';
const listeners = [];

export function t(key) {
  return dicts[lang][key] ?? key;
}

export function getLang() {
  return lang;
}

export function toggleLang() {
  lang = lang === 'id' ? 'en' : 'id';
  listeners.forEach((fn) => fn(lang));
}

export function onLangChange(fn) {
  listeners.push(fn);
}
