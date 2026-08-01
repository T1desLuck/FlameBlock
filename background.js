importScripts('common.js');

// ---------------------------------------------------------------------------
// Бейдж и счётчики заблокированного (per-tab, живёт в chrome.storage.session,
// а не в обычной переменной — service worker может перезапускаться в любой
// момент, и обычный массив/Map в памяти просто исчезнет).
// ---------------------------------------------------------------------------

async function fbGetTabCount(tabId) {
  const key = 'tabCount_' + tabId;
  const data = await chrome.storage.session.get({ [key]: 0 });
  return data[key];
}

async function fbSetTabCount(tabId, value) {
  const key = 'tabCount_' + tabId;
  await chrome.storage.session.set({ [key]: value });
  try {
    await chrome.action.setBadgeText({ tabId, text: value > 0 ? fbFormatCount(value) : '' });
    await chrome.action.setBadgeBackgroundColor({ tabId, color: FB_BADGE_COLOR });
    if (chrome.action.setBadgeTextColor) {
      await chrome.action.setBadgeTextColor({ tabId, color: '#ffffff' });
    }
  } catch (e) {
    // вкладка уже могла закрыться — не страшно
  }
}

async function fbIncrementTabCount(tabId, amount) {
  if (tabId == null || tabId < 0 || !amount) return;
  const settings = await fbGetSettings();
  if (!settings.masterEnabled) return;
  const current = await fbGetTabCount(tabId);
  await fbSetTabCount(tabId, current + amount);
  await fbSetSettings({ totalBlocked: (settings.totalBlocked || 0) + amount });
}

// Отдельный, изолированный счётчик именно для эвристики по размеру iframe —
// нужен, чтобы человек мог наглядно увидеть, что функция реально что-то
// ловит, а не гадать по общему числу (там всё смешано с списками и CSS).
async function fbGetIframeHeuristicCount(tabId) {
  const key = 'iframeHeuristicCount_' + tabId;
  const data = await chrome.storage.session.get({ [key]: 0 });
  return data[key];
}

async function fbSetIframeHeuristicCount(tabId, value) {
  const key = 'iframeHeuristicCount_' + tabId;
  await chrome.storage.session.set({ [key]: value });
}

async function fbIncrementIframeHeuristicCount(tabId, amount) {
  if (tabId == null || tabId < 0 || !amount) return;
  const current = await fbGetIframeHeuristicCount(tabId);
  await fbSetIframeHeuristicCount(tabId, current + amount);
}

chrome.webNavigation.onBeforeNavigate.addListener((details) => {
  if (details.frameId === 0) {
    fbSetTabCount(details.tabId, 0);
    fbSetIframeHeuristicCount(details.tabId, 0);
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  chrome.storage.session.remove('tabCount_' + tabId);
  chrome.storage.session.remove('iframeHeuristicCount_' + tabId);
});

// Наблюдаем (не блокируем — блокировку делает DNR) за сетевыми запросами,
// которые браузер оборвал по правилу расширения, чтобы вести счёт.
chrome.webRequest.onErrorOccurred.addListener(
  (details) => {
    if (details.error === 'net::ERR_BLOCKED_BY_CLIENT' && details.tabId >= 0) {
      fbIncrementTabCount(details.tabId, 1);
    }
  },
  { urls: ['<all_urls>'] }
);

// ---------------------------------------------------------------------------
// Вайт-лист сайтов через динамические правила DNR (приоритет 2 — выше,
// чем базовые списки блокировки с приоритетом 1, поэтому allow-правило
// побеждает для всех запросов, инициированных с этого хоста).
// ---------------------------------------------------------------------------

async function fbSetSiteEnabled(hostname, enabled) {
  const settings = await fbGetSettings();
  const whitelist = settings.whitelist || [];
  const ruleIds = settings.whitelistRuleIds || {};

  if (!enabled) {
    if (!whitelist.includes(hostname)) {
      const ruleId = await fbAllocateRuleId();
      ruleIds[hostname] = ruleId;
      whitelist.push(hostname);
      await chrome.declarativeNetRequest.updateDynamicRules({
        addRules: [{
          id: ruleId,
          priority: 2,
          action: { type: 'allow' },
          condition: {
            initiatorDomains: [hostname],
            resourceTypes: ['main_frame', 'sub_frame', 'script', 'image', 'xmlhttprequest',
                             'media', 'font', 'object', 'ping', 'other', 'websocket', 'stylesheet']
          }
        }]
      });
    }
  } else {
    const ruleId = ruleIds[hostname];
    const idx = whitelist.indexOf(hostname);
    if (idx >= 0) whitelist.splice(idx, 1);
    delete ruleIds[hostname];
    if (ruleId) {
      await chrome.declarativeNetRequest.updateDynamicRules({ removeRuleIds: [ruleId] });
    }
  }
  await fbSetSettings({ whitelist, whitelistRuleIds: ruleIds });
}

// ---------------------------------------------------------------------------
// MAIN-world скрипты — статический JS, встраивается в контекст страницы (не
// в изолированный мир расширения) через chrome.scripting. Включаем/выключаем
// саму РЕГИСТРАЦИЮ в зависимости от настроек, а не логику внутри скрипта —
// сами файлы остаются маленькими статичными файлами без chrome.* API (в MAIN
// world этого API просто нет, это ограничение платформы). scriptlets.js
// (гейт на попандеры) и fingerprint-protect.js (шум в Canvas/WebGL/Audio) —
// это две РАЗНЫЕ функции с разными настройками, регистрируются независимо.
// ---------------------------------------------------------------------------

const FB_SCRIPTLETS_ID = 'flameblock-scriptlets';
const FB_FINGERPRINT_ID = 'flameblock-fingerprint-protect';

// Свежая регистрация MAIN-world скрипта распространяется только на СЛЕДУЮЩИЕ
// загрузки страниц — уже открытые вкладки её не подхватят сами по себе,
// пользователю пришлось бы вручную перезагружать каждую вкладку. Чтобы
// защита начинала работать сразу, как только включена настройка, инъецируем
// скрипт и в уже открытые вкладки напрямую.
async function fbInjectIntoOpenTabs(file) {
  let tabs = [];
  try {
    tabs = await chrome.tabs.query({ url: ['http://*/*', 'https://*/*'] });
  } catch (e) { return; }
  for (const tab of tabs) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id, allFrames: true },
        world: 'MAIN',
        files: [file],
      });
    } catch (e) { /* вкладка недоступна для инъекции (служебная страница и т.п.) — не страшно */ }
  }
}

async function fbSyncMainWorldScript(id, file, shouldRun) {
  let existing = [];
  try {
    existing = await chrome.scripting.getRegisteredContentScripts({ ids: [id] });
  } catch (e) { /* API может быть недоступен в очень старых сборках — не критично */ }

  if (shouldRun && existing.length === 0) {
    try {
      await chrome.scripting.registerContentScripts([{
        id, matches: ['<all_urls>'], js: [file], runAt: 'document_start', world: 'MAIN', allFrames: true
      }]);
      await fbInjectIntoOpenTabs(file);
    } catch (e) { /* уже зарегистрирован в другом воркере — не страшно */ }
  } else if (!shouldRun && existing.length > 0) {
    try {
      await chrome.scripting.unregisterContentScripts({ ids: [id] });
    } catch (e) { /* уже снят — не страшно */ }
  }
}

async function fbSyncScriptlets() {
  const settings = await fbGetSettings();
  await fbSyncMainWorldScript(FB_SCRIPTLETS_ID, 'scriptlets.js', settings.masterEnabled && settings.stealthMode);
  await fbSyncMainWorldScript(FB_FINGERPRINT_ID, 'fingerprint-protect.js', settings.masterEnabled && settings.fingerprintProtection);
  await fbSyncWebRTCPolicy(settings);
}

// Утечка WebRTC — не JS-подмена на странице, а официальная настройка самого
// браузера (chrome.privacy), которая надёжнее любого перехвата в скрипте.
// По умолчанию выключено: полное экранирование ломает видеозвонки в браузере
// (Google Meet и подобные), поэтому это осознанный выбор пользователя.
async function fbSyncWebRTCPolicy(settingsArg) {
  const settings = settingsArg || await fbGetSettings();
  const enabled = settings.masterEnabled && settings.webrtcProtection;
  const policy = enabled ? 'disable_non_proxied_udp' : 'default';
  try {
    if (chrome.privacy && chrome.privacy.network && chrome.privacy.network.webRTCIPHandlingPolicy) {
      await chrome.privacy.network.webRTCIPHandlingPolicy.set({ value: policy });
    }
  } catch (e) { /* политика может быть недоступна (управляется администратором и т.п.) — не критично */ }
}

// ---------------------------------------------------------------------------
// Пользовательские правила (продвинутые настройки): построчно, "domain" —
// блокировать, "@@domain" — явно разрешить. Хранятся с собственным ruleId,
// приоритет 3 — выше и списков, и вайт-листа сайта (явное правило важнее).
// ---------------------------------------------------------------------------

function fbParseCustomLine(line) {
  line = line.trim();
  if (!line || line.startsWith('!') || line.startsWith('#')) return null;
  let type = 'block';
  if (line.startsWith('@@')) {
    type = 'allow';
    line = line.slice(2);
  }
  line = line.replace(/^\|\|/, '').replace(/\^$/, '').trim();
  if (!line || !/^[a-zA-Z0-9.\-]+$/.test(line)) return null;
  return { type, domain: line.toLowerCase() };
}

async function fbSaveCustomRules(rawText) {
  const settings = await fbGetSettings();
  const oldIds = (settings.customRules || []).map(r => r.ruleId);
  if (oldIds.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ removeRuleIds: oldIds });
  }

  const lines = rawText.split('\n');
  const newRules = [];
  const dnrAdd = [];
  for (const line of lines) {
    const parsed = fbParseCustomLine(line);
    if (!parsed) continue;
    const ruleId = await fbAllocateRuleId();
    newRules.push({ ruleId, type: parsed.type, text: parsed.domain });
    dnrAdd.push({
      id: ruleId,
      priority: 3,
      action: { type: parsed.type === 'allow' ? 'allow' : 'block' },
      condition: {
        urlFilter: `||${parsed.domain}^`,
        resourceTypes: ['main_frame', 'sub_frame', 'script', 'image', 'xmlhttprequest',
                         'media', 'font', 'object', 'ping', 'other', 'websocket', 'stylesheet']
      }
    });
  }

  if (dnrAdd.length) {
    await chrome.declarativeNetRequest.updateDynamicRules({ addRules: dnrAdd });
  }
  await fbSetSettings({ customRules: newRules });
  return newRules.length;
}

// ---------------------------------------------------------------------------
// Сообщения от popup / options / content-скриптов
// ---------------------------------------------------------------------------

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    switch (message?.type) {
      case 'COSMETIC_HIDE_COUNT': {
        if (sender.tab) await fbIncrementTabCount(sender.tab.id, message.count || 0);
        sendResponse({ ok: true });
        break;
      }
      case 'SCRIPTLET_DEFUSE_COUNT': {
        if (sender.tab) await fbIncrementTabCount(sender.tab.id, message.count || 0);
        sendResponse({ ok: true });
        break;
      }
      case 'IFRAME_HEURISTIC_COUNT': {
        if (sender.tab) {
          await fbIncrementTabCount(sender.tab.id, message.count || 0);
          await fbIncrementIframeHeuristicCount(sender.tab.id, message.count || 0);
        }
        sendResponse({ ok: true });
        break;
      }
      case 'GET_SITE_INFO': {
        const settings = await fbGetSettings();
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const hostname = tab ? fbGetHostname(tab.url) : '';
        const isWhitelisted = fbHostnameInList(settings.whitelist, hostname);
        const count = tab ? await fbGetTabCount(tab.id) : 0;
        const iframeHeuristicCount = tab ? await fbGetIframeHeuristicCount(tab.id) : 0;
        sendResponse({
          hostname,
          siteEnabled: settings.masterEnabled && !isWhitelisted,
          masterEnabled: settings.masterEnabled,
          count,
          totalBlocked: settings.totalBlocked || 0,
          heuristicIframesOn: !!settings.heuristicIframes,
          iframeHeuristicCount
        });
        break;
      }
      case 'SET_SITE_ENABLED': {
        await fbSetSiteEnabled(message.hostname, message.enabled);
        sendResponse({ ok: true });
        break;
      }
      case 'SET_MASTER_ENABLED': {
        await fbSetSettings({ masterEnabled: message.enabled });
        await fbSyncScriptlets();
        sendResponse({ ok: true });
        break;
      }
      case 'GET_SETTINGS': {
        sendResponse(await fbGetSettings());
        break;
      }
      case 'SET_SETTINGS': {
        await fbSetSettings(message.settings || {});
        await fbSyncScriptlets();
        sendResponse({ ok: true });
        break;
      }
      case 'REMOVE_FROM_WHITELIST': {
        await fbSetSiteEnabled(message.hostname, true);
        sendResponse({ ok: true });
        break;
      }
      case 'SAVE_CUSTOM_RULES': {
        const count = await fbSaveCustomRules(message.text || '');
        sendResponse({ ok: true, count });
        break;
      }
      default:
        sendResponse({ ok: false });
    }
  })();
  return true; // отвечаем асинхронно
});

chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason === 'install') {
    await fbSetSettings({ installDate: Date.now() });
  }
  await fbSyncScriptlets();
});

chrome.runtime.onStartup.addListener(() => {
  fbSyncScriptlets();
});
