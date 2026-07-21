// common.js — общие функции и настройки по умолчанию.
// Подключается и в background.js (через importScripts), и в popup/options (через <script>).

const FB_BADGE_COLOR = '#b52b0e';

const FB_DEFAULTS = {
  masterEnabled: true,       // общий выключатель расширения
  blockAds: true,             // блокировка рекламных сетей
  blockTrackers: true,        // блокировка трекеров/аналитики
  stealthMode: true,          // обход анти-adblock скриптов
  cosmeticFiltering: true,    // скрытие рекламных блоков через CSS
  heuristicIframes: false,    // экспериментально: скрывать iframe рекламных размеров с чужого домена
  languageOverride: '',       // код языка, выбранный пользователем вручную ('' = автоопределение)
  whitelist: [],              // хосты, где реклама разрешена по желанию пользователя
  whitelistRuleIds: {},       // { hostname: dynamicRuleId } — для снятия allow-правил DNR
  customRules: [],            // [{ id, ruleId, type: 'block'|'allow', text }]
  nextDynamicRuleId: 1000,    // счётчик для выдачи уникальных id динамических правил
  totalBlocked: 0,            // счётчик всего заблокированного за всё время
  installDate: 0
};

function fbGetHostname(url) {
  try {
    const u = new URL(url);
    if (!/^https?:$/.test(u.protocol)) return '';
    return u.hostname;
  } catch (e) {
    return '';
  }
}

function fbHostnameInList(list, hostname) {
  if (!hostname) return false;
  return list.some(h => hostname === h || hostname.endsWith('.' + h));
}

async function fbGetSettings() {
  const data = await chrome.storage.local.get(FB_DEFAULTS);
  return data;
}

async function fbSetSettings(partial) {
  await chrome.storage.local.set(partial);
}

async function fbAllocateRuleId() {
  const { nextDynamicRuleId } = await chrome.storage.local.get({ nextDynamicRuleId: FB_DEFAULTS.nextDynamicRuleId });
  await chrome.storage.local.set({ nextDynamicRuleId: nextDynamicRuleId + 1 });
  return nextDynamicRuleId;
}

function fbFormatCount(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace('.0', '') + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1).replace('.0', '') + 'K';
  return String(n);
}
