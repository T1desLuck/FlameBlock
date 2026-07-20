let currentTabId = null;
let fbT = (key) => key;

const hostnameEl = document.getElementById('hostname');
const siteToggleEl = document.getElementById('siteToggle');
const siteStatusEl = document.getElementById('siteStatus');
const pageCountEl = document.getElementById('pageCount');
const totalCountEl = document.getElementById('totalCount');
const pauseBtn = document.getElementById('pauseBtn');
const reloadBtn = document.getElementById('reloadBtn');
const settingsBtn = document.getElementById('settingsBtn');

async function refresh() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTabId = tab ? tab.id : null;

  const info = await chrome.runtime.sendMessage({ type: 'GET_SITE_INFO' });
  if (!info) return;

  hostnameEl.textContent = info.hostname || '—';
  hostnameEl.title = info.hostname || '';
  pageCountEl.textContent = fbFormatCount(info.count || 0);
  totalCountEl.textContent = fbFormatCount(info.totalBlocked || 0);

  siteToggleEl.checked = info.siteEnabled;
  siteStatusEl.textContent = info.siteEnabled ? fbT('protection_on') : fbT('ads_allowed_here');
  siteStatusEl.classList.toggle('off', !info.siteEnabled);

  pauseBtn.classList.toggle('is-paused', !info.masterEnabled);
  pauseBtn.title = info.masterEnabled ? fbT('pause_all_title') : fbT('resume_protection_title');

  const noHost = !info.hostname;
  siteToggleEl.disabled = noHost;
}

siteToggleEl.addEventListener('change', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const hostname = tab ? fbGetHostname(tab.url) : '';
  if (!hostname) return;
  await chrome.runtime.sendMessage({ type: 'SET_SITE_ENABLED', hostname, enabled: siteToggleEl.checked });
  if (tab) chrome.tabs.reload(tab.id);
  window.close();
});

pauseBtn.addEventListener('click', async () => {
  const settings = await chrome.runtime.sendMessage({ type: 'GET_SETTINGS' });
  const nextEnabled = !settings.masterEnabled;
  await chrome.runtime.sendMessage({ type: 'SET_MASTER_ENABLED', enabled: nextEnabled });
  if (currentTabId != null) chrome.tabs.reload(currentTabId);
  await refresh();
});

reloadBtn.addEventListener('click', async () => {
  if (currentTabId != null) chrome.tabs.reload(currentTabId);
  window.close();
});

settingsBtn.addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
});

(async () => {
  const i18n = await fbApplyI18n();
  fbT = i18n.t;
  await refresh();
})();
