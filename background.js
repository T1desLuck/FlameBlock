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

chrome.webNavigation.onBeforeNavigate.addListener((details) => {
  if (details.frameId === 0) {
    fbSetTabCount(details.tabId, 0);
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  chrome.storage.session.remove('tabCount_' + tabId);
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
// scriptlets.js — статический JS, встраивается в MAIN world страницы (не в
// изолированный мир расширения) через chrome.scripting. Включаем/выключаем
// саму РЕГИСТРАЦИЮ в зависимости от настроек, а не логику внутри скрипта —
// так scriptlets.js остаётся маленьким статичным файлом без chrome.* API
// (в MAIN world этого API просто нет, это ограничение платформы).
// ---------------------------------------------------------------------------

const FB_SCRIPTLETS_ID = 'flameblock-scriptlets';

async function fbSyncScriptlets() {
  const settings = await fbGetSettings();
  const shouldRun = settings.masterEnabled && settings.stealthMode;
  let existing = [];
  try {
    existing = await chrome.scripting.getRegisteredContentScripts({ ids: [FB_SCRIPTLETS_ID] });
  } catch (e) { /* API может быть недоступен в очень старых сборках — не критично */ }

  if (shouldRun && existing.length === 0) {
    try {
      await chrome.scripting.registerContentScripts([{
        id: FB_SCRIPTLETS_ID,
        matches: ['<all_urls>'],
        js: ['scriptlets.js'],
        runAt: 'document_start',
        world: 'MAIN',
        allFrames: true
      }]);
    } catch (e) { /* уже зарегистрирован в другом воркере — не страшно */ }
  } else if (!shouldRun && existing.length > 0) {
    try {
      await chrome.scripting.unregisterContentScripts({ ids: [FB_SCRIPTLETS_ID] });
    } catch (e) { /* уже снят — не страшно */ }
  }
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
      case 'GET_SITE_INFO': {
        const settings = await fbGetSettings();
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const hostname = tab ? fbGetHostname(tab.url) : '';
        const isWhitelisted = fbHostnameInList(settings.whitelist, hostname);
        const count = tab ? await fbGetTabCount(tab.id) : 0;
        sendResponse({
          hostname,
          siteEnabled: settings.masterEnabled && !isWhitelisted,
          masterEnabled: settings.masterEnabled,
          count,
          totalBlocked: settings.totalBlocked || 0
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
