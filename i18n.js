// i18n.js — определение активного языка и применение переводов к DOM.
// Подключается после common.js и до popup.js/options.js в popup.html и options.html.
//
// Порядок определения языка (как в большинстве приложений):
//   1. Явный выбор пользователя в настройках (chrome.storage.local.languageOverride)
//   2. Язык браузера/ОС (chrome.i18n.getUILanguage()), если он среди поддерживаемых
//   3. Русский — запасной вариант по умолчанию

const FB_SUPPORTED_LOCALES = ['ru', 'en', 'zh_CN', 'es', 'hi', 'ar', 'pt_BR', 'ja', 'ko', 'de', 'fr', 'id'];
const FB_DEFAULT_LOCALE = 'ru';
const FB_RTL_LOCALES = ['ar'];

function fbNormalizeLocale(raw) {
  if (!raw) return '';
  const norm = raw.replace('-', '_');
  if (FB_SUPPORTED_LOCALES.includes(norm)) return norm;
  const base = norm.split('_')[0];
  return FB_SUPPORTED_LOCALES.find(l => l.split('_')[0] === base) || '';
}

function fbDetectSystemLocale() {
  const raw = (typeof chrome !== 'undefined' && chrome.i18n && chrome.i18n.getUILanguage)
    ? chrome.i18n.getUILanguage()
    : (navigator.language || '');
  return fbNormalizeLocale(raw) || FB_DEFAULT_LOCALE;
}

async function fbGetActiveLocale() {
  const { languageOverride } = await chrome.storage.local.get({ languageOverride: '' });
  if (languageOverride && FB_SUPPORTED_LOCALES.includes(languageOverride)) return languageOverride;
  return fbDetectSystemLocale();
}

// В BCP-47 виде — для Date/Number toLocaleString и т.п.
function fbToBcp47(locale) {
  return locale.replace('_', '-');
}

const fbMessagesCache = {};
async function fbLoadMessages(locale) {
  if (fbMessagesCache[locale]) return fbMessagesCache[locale];
  try {
    const url = chrome.runtime.getURL(`_locales/${locale}/messages.json`);
    const res = await fetch(url);
    const data = await res.json();
    const flat = {};
    for (const key in data) flat[key] = data[key].message;
    fbMessagesCache[locale] = flat;
    return flat;
  } catch (e) {
    return {};
  }
}

// Возвращает { locale, t } — locale активного языка и функцию перевода t(key, vars).
// vars — необязательный объект для подстановки вида {name} внутри строки перевода.
async function fbApplyI18n(root) {
  root = root || document;
  const locale = await fbGetActiveLocale();
  const messages = await fbLoadMessages(locale);
  const fallback = locale !== FB_DEFAULT_LOCALE ? await fbLoadMessages(FB_DEFAULT_LOCALE) : messages;

  function t(key, vars) {
    let str = messages[key] || fallback[key] || key;
    if (vars) {
      for (const k in vars) str = str.split('{' + k + '}').join(vars[k]);
    }
    return str;
  }

  root.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  root.querySelectorAll('[data-i18n-html]').forEach((el) => {
    el.innerHTML = t(el.getAttribute('data-i18n-html'));
  });
  root.querySelectorAll('[data-i18n-title]').forEach((el) => {
    el.setAttribute('title', t(el.getAttribute('data-i18n-title')));
  });
  root.querySelectorAll('[data-i18n-aria-label]').forEach((el) => {
    el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria-label')));
  });
  root.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    el.setAttribute('placeholder', t(el.getAttribute('data-i18n-placeholder')));
  });

  document.documentElement.setAttribute('lang', locale.split('_')[0]);
  document.documentElement.setAttribute('dir', FB_RTL_LOCALES.includes(locale) ? 'rtl' : 'ltr');

  return { locale, t };
}
