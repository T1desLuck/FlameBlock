let currentTabId = null;
let currentHostname = '';
let fbT = (key) => key;

const hostnameEl = document.getElementById('hostname');
const siteFaviconEl = document.getElementById('siteFavicon');
const statusDotEl = document.getElementById('statusDot');
const siteToggleEl = document.getElementById('siteToggle');
const siteStatusEl = document.getElementById('siteStatus');
const pageCountEl = document.getElementById('pageCount');
const totalCountEl = document.getElementById('totalCount');
const pauseBtn = document.getElementById('pauseBtn');
const reloadBtn = document.getElementById('reloadBtn');
const reportBtn = document.getElementById('reportBtn');
const settingsBtn = document.getElementById('settingsBtn');
const iframeHeuristicRow = document.getElementById('iframeHeuristicRow');
const iframeHeuristicCountEl = document.getElementById('iframeHeuristicCount');

function faviconUrl(pageUrl) {
  const url = new URL(chrome.runtime.getURL('/_favicon/'));
  url.searchParams.set('pageUrl', pageUrl);
  url.searchParams.set('size', '32');
  return url.toString();
}

async function refresh() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTabId = tab ? tab.id : null;

  const info = await chrome.runtime.sendMessage({ type: 'GET_SITE_INFO' });
  if (!info) return;

  currentHostname = info.hostname || '';
  hostnameEl.textContent = info.hostname || '—';
  hostnameEl.title = info.hostname || '';
  pageCountEl.textContent = fbFormatCount(info.count || 0);
  totalCountEl.textContent = fbFormatCount(info.totalBlocked || 0);

  if (tab && tab.url) {
    siteFaviconEl.src = faviconUrl(tab.url);
    siteFaviconEl.hidden = false;
    siteFaviconEl.onerror = () => { siteFaviconEl.hidden = true; };
  } else {
    siteFaviconEl.hidden = true;
  }

  siteToggleEl.checked = info.siteEnabled;
  siteStatusEl.textContent = info.siteEnabled ? fbT('protection_on') : fbT('ads_allowed_here');
  siteStatusEl.classList.toggle('off', !info.siteEnabled);
  statusDotEl.classList.toggle('off', !info.siteEnabled);

  pauseBtn.classList.toggle('is-paused', !info.masterEnabled);
  pauseBtn.title = info.masterEnabled ? fbT('pause_all_title') : fbT('resume_protection_title');

  const noHost = !info.hostname;
  siteToggleEl.disabled = noHost;
  reportBtn.disabled = noHost;

  // Показываем счётчик эвристики iframe только когда сама функция включена
  // в настройках — так сразу видно и что она работает, и сколько поймала
  // именно на этой странице (не смешано с остальными способами блокировки).
  iframeHeuristicRow.hidden = !info.heuristicIframesOn;
  if (info.heuristicIframesOn) {
    iframeHeuristicCountEl.textContent = fbFormatCount(info.iframeHeuristicCount || 0);
  }
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

reportBtn.addEventListener('click', () => {
  if (!currentHostname) return;
  const subject = fbT('report_issue_subject', { site: currentHostname });
  const body = fbT('report_issue_body', { site: currentHostname });
  const mailto = 'mailto:tidesluck@icloud.com'
    + '?subject=' + encodeURIComponent(subject)
    + '&body=' + encodeURIComponent(body);
  window.open(mailto);
  window.close();
});

settingsBtn.addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
});

(async () => {
  await fbInitTheme();

  const i18n = await fbApplyI18n();
  fbT = i18n.t;
  await refresh();
})();
