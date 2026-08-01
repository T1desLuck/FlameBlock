let fbT = (key) => key;
let fbActiveLocale = FB_DEFAULT_LOCALE;

const toggleIds = ['masterEnabled', 'blockAds', 'blockTrackers', 'stealthMode', 'cosmeticFiltering', 'heuristicIframes', 'fingerprintProtection', 'webrtcProtection'];
const els = {};
toggleIds.forEach(id => { els[id] = document.getElementById(id); });

const statTotal = document.getElementById('statTotal');
const statSince = document.getElementById('statSince');
const whitelistUl = document.getElementById('whitelistUl');
const whitelistEmpty = document.getElementById('whitelistEmpty');
const customRulesEl = document.getElementById('customRules');
const saveRulesBtn = document.getElementById('saveRulesBtn');
const rulesSaved = document.getElementById('rulesSaved');
const languageSelect = document.getElementById('languageSelect');
const accordionItems = document.querySelectorAll('.accordion-item');
const themeToggle = document.getElementById('themeToggle');
const navButtons = document.querySelectorAll('.nav-btn');
const panels = document.querySelectorAll('.panel');

navButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.panel;
    navButtons.forEach((b) => b.classList.toggle('is-active', b === btn));
    panels.forEach((p) => p.classList.toggle('is-active', p.id === target));
  });
});

themeToggle.addEventListener('click', async () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  fbApplyTheme(next);
  await chrome.storage.local.set({ themePreference: next });
});

function syncOpenPanelHeights() {
  // При смене языка текст внутри открытых панелей может стать длиннее или
  // короче — пересчитываем высоту, чтобы не обрезалось и не оставалось пустого места.
  accordionItems.forEach((item) => {
    if (item.classList.contains('is-open')) {
      const panel = item.querySelector('.accordion-panel');
      panel.style.maxHeight = panel.scrollHeight + 'px';
    }
  });
}

accordionItems.forEach((item) => {
  const trigger = item.querySelector('.accordion-trigger');
  const panel = item.querySelector('.accordion-panel');
  trigger.addEventListener('click', () => {
    const isOpen = item.classList.toggle('is-open');
    trigger.setAttribute('aria-expanded', String(isOpen));
    panel.style.maxHeight = isOpen ? panel.scrollHeight + 'px' : '0px';
  });
});

function formatDate(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleDateString(fbToBcp47(fbActiveLocale), { day: 'numeric', month: 'long', year: 'numeric' });
}

async function load() {
  const settings = await chrome.runtime.sendMessage({ type: 'GET_SETTINGS' });

  toggleIds.forEach(id => { els[id].checked = !!settings[id]; });
  languageSelect.value = settings.languageOverride || '';

  statTotal.textContent = (settings.totalBlocked || 0).toLocaleString(fbToBcp47(fbActiveLocale));
  statSince.textContent = formatDate(settings.installDate);

  const whitelist = settings.whitelist || [];
  whitelistUl.innerHTML = '';
  whitelistEmpty.style.display = whitelist.length ? 'none' : 'block';
  for (const host of whitelist) {
    const li = document.createElement('li');
    const span = document.createElement('span');
    span.textContent = host;
    const btn = document.createElement('button');
    btn.className = 'remove-btn';
    btn.textContent = fbT('remove_button');
    btn.addEventListener('click', async () => {
      await chrome.runtime.sendMessage({ type: 'REMOVE_FROM_WHITELIST', hostname: host });
      load();
    });
    li.appendChild(span);
    li.appendChild(btn);
    whitelistUl.appendChild(li);
  }

  const customText = (settings.customRules || []).map(r => (r.type === 'allow' ? '@@' : '') + r.text).join('\n');
  customRulesEl.value = customText;
}

toggleIds.forEach(id => {
  els[id].addEventListener('change', async () => {
    await chrome.runtime.sendMessage({ type: 'SET_SETTINGS', settings: { [id]: els[id].checked } });
  });
});

languageSelect.addEventListener('change', async () => {
  await chrome.runtime.sendMessage({ type: 'SET_SETTINGS', settings: { languageOverride: languageSelect.value } });
  const i18n = await fbApplyI18n();
  fbT = i18n.t;
  fbActiveLocale = i18n.locale;
  await load();
  syncOpenPanelHeights();
});

saveRulesBtn.addEventListener('click', async () => {
  const res = await chrome.runtime.sendMessage({ type: 'SAVE_CUSTOM_RULES', text: customRulesEl.value });
  if (res && res.ok) {
    rulesSaved.textContent = fbT('rules_saved', { count: res.count });
    rulesSaved.classList.add('show');
    setTimeout(() => rulesSaved.classList.remove('show'), 2200);
  }
});

(async () => {
  await fbInitTheme();

  const i18n = await fbApplyI18n();
  fbT = i18n.t;
  fbActiveLocale = i18n.locale;
  await load();
})();
