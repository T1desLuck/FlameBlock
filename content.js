// content.js — косметическое скрытие рекламных блоков (ISOLATED world).
// Три независимых слоя:
//   1. CSS-селекторы по известным паттернам рекламных движков (как в v1.0.0)
//   2. Текстовая эвристика: короткие метки "Реклама"/"Sponsored" -> прячем
//      контейнер-обёртку на пару уровней выше (упрощённый аналог uBO :has-text()+:upward())
//   3. Эвристика по размеру iframe (выключена по умолчанию, см. options)
// Плюс приём событий от scriptlets.js (MAIN world) через CustomEvent на document.

(function () {
  if (window.__fbInjected) return;
  window.__fbInjected = true;

  const AD_SELECTORS = [
    '.adsbygoogle', 'ins.adsbygoogle',
    '[id^="google_ads_iframe"]', '[id^="google_ads_frame"]',
    '[id^="div-gpt-ad"]', '[id*="/gpt-ad"]',
    'iframe[id^="google_ads_iframe"]',
    'iframe[src*="doubleclick.net"]', 'iframe[src*="googlesyndication.com"]',
    '[data-ad-slot]', '[data-ad-client]',
    '[class^="ad-container"]', '[class*=" ad-container"]',
    '[class^="ads-container"]', '[id^="ad-container"]',
    '[class^="banner-ad"]', '[class*=" banner-ad"]', '[id^="banner-ad"]',
    '.ad-slot', '.ads-slot',
    '[class^="advertisement"]', '[id^="advertisement"]',
    '.text-ad', '.textad',
    '[class*="sponsored-content"]',
    '.taboola', '[id*="taboola"]',
    '.outbrain', '[id*="outbrain"]', '.OUTBRAIN',
    'ins.adsbyexoclick',
    '[class^="mgid"]',
    '[aria-label="Advertisement"]', '[aria-label="Реклама"]',
    '.yandex-rtb', '[id^="yandex_rtb"]', '[id^="yandex_ad"]', '[id^="R-A-"]',
    'div[id^="ad_"]', 'div[class^="ad_"]',
    '.google-auto-placed',
    // cookie-consent баннеры (CMP) — самая слабая категория по тестам
    '#onetrust-banner-sdk', '#onetrust-consent-sdk', '.onetrust-pc-dark-filter',
    '#CybotCookiebotDialog', '#CybotCookiebotDialogBodyUnderlay',
    '.qc-cmp2-container', '#didomi-host', '#usercentrics-root',
    '[id^="cookiescript_"]', '[class*="cookie-consent"]', '[class*="cookie-banner"]',
    '[class*="consent-banner"]', '[id*="consent-banner"]', '.cc-window', '.cc-banner',
    // точные "приманки", которые используют тестовые сайты (turtlecute.org и т.п.)
    // для проверки самого факта работы косметической фильтрации
    '.adsbox', '.banner_ads', '.adbox', '.ADBox', '.AdBox', '.adbox-wrapper',
    '.adSocial', '.ad-unit', '.afs_ads', '.ad-zone', '.ad-space', '#ad_ctd',
    '#Adcolony', '#hostListAdblock',
  ].join(', ');

  // Короткие самостоятельные метки спонсорского контента. Намеренно требуем
  // почти точное совпадение и короткую длину текста — иначе можно случайно
  // скрыть статью, которая просто упоминает слово "реклама" в тексте.
  const SPONSORED_LABEL_RE = /^(реклама\s*\d{0,2}\+?|sponsored( content)?|advertisement|advertising|promoted( content)?|на правах рекламы|партнёрский материал)$/i;

  const AD_IFRAME_SIZES = [
    [300, 250], [728, 90], [320, 50], [160, 600], [970, 250],
    [300, 600], [336, 280], [320, 100], [300, 50], [250, 250]
  ];

  let styleEl = null;
  let observer = null;
  let hiddenCount = 0;
  let siteActive = true;
  let heuristicIframesOn = false;
  let scanTimer = null;

  const checkedLabelNodes = new WeakSet();
  const checkedIframes = new WeakSet();

  function reportDelta(n) {
    if (!n) return;
    hiddenCount += n;
    chrome.runtime.sendMessage({ type: 'COSMETIC_HIDE_COUNT', count: n }).catch(() => {});
  }

  function injectStyle() {
    if (styleEl) return;
    styleEl = document.createElement('style');
    styleEl.setAttribute('data-flameblock', '1');
    styleEl.textContent = AD_SELECTORS + ' { display: none !important; visibility: hidden !important; }';
    (document.head || document.documentElement).appendChild(styleEl);
  }

  function removeStyle() {
    if (styleEl) { styleEl.remove(); styleEl = null; }
  }

  // Отдельный счётчик "сколько уже совпало по селекторам" — держим отдельно
  // от общего hiddenCount, чтобы не путать источники подсчёта.
  let lastSelectorMatch = 0;
  function scanSelectorsSafe() {
    let matched = 0;
    try { matched = document.querySelectorAll(AD_SELECTORS).length; } catch (e) { /* noop */ }
    if (matched > lastSelectorMatch) {
      reportDelta(matched - lastSelectorMatch);
      lastSelectorMatch = matched;
    }
  }

  function scanTextLabels() {
    const candidates = document.querySelectorAll('div, span, p, a, small');
    let delta = 0;
    for (const el of candidates) {
      if (checkedLabelNodes.has(el)) continue;
      checkedLabelNodes.add(el);
      if (el.children.length > 0) continue;
      const text = (el.textContent || '').trim();
      if (!text || text.length > 40) continue;
      if (!SPONSORED_LABEL_RE.test(text)) continue;
      let target = el;
      for (let i = 0; i < 2 && target.parentElement && target.parentElement !== document.body; i++) {
        target = target.parentElement;
      }
      if (target && target.style.display !== 'none') {
        target.style.setProperty('display', 'none', 'important');
        delta++;
      }
    }
    reportDelta(delta);
  }

  function scanAdSizedIframes() {
    if (!heuristicIframesOn) return;
    const frames = document.querySelectorAll('iframe');
    let delta = 0;
    for (const f of frames) {
      if (checkedIframes.has(f)) continue;
      checkedIframes.add(f);
      const w = parseInt(f.getAttribute('width') || f.offsetWidth, 10);
      const h = parseInt(f.getAttribute('height') || f.offsetHeight, 10);
      if (!w || !h) continue;
      const isAdSize = AD_IFRAME_SIZES.some(([aw, ah]) => Math.abs(w - aw) <= 2 && Math.abs(h - ah) <= 2);
      if (!isAdSize) continue;
      let crossOrigin = false;
      try {
        const src = f.getAttribute('src');
        if (src) crossOrigin = new URL(src, location.href).hostname !== location.hostname;
      } catch (e) { /* noop */ }
      if (crossOrigin) {
        f.style.setProperty('display', 'none', 'important');
        delta++;
      }
    }
    reportDelta(delta);
  }

  function runScan() {
    if (!siteActive) return;
    scanSelectorsSafe();
    scanTextLabels();
    scanAdSizedIframes();
  }

  function scheduleScan() {
    if (scanTimer) return;
    scanTimer = setTimeout(() => {
      scanTimer = null;
      runScan();
    }, 400);
  }

  function startObserving() {
    if (observer) return;
    observer = new MutationObserver(() => scheduleScan());
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  function stopObserving() {
    if (observer) { observer.disconnect(); observer = null; }
  }

  async function getState() {
    const { masterEnabled, cosmeticFiltering, heuristicIframes, whitelist } = await chrome.storage.local.get({
      masterEnabled: true, cosmeticFiltering: true, heuristicIframes: false, whitelist: []
    });
    const hostname = location.hostname;
    const whitelisted = whitelist.some(h => hostname === h || hostname.endsWith('.' + h));
    return {
      active: masterEnabled && cosmeticFiltering && !whitelisted,
      heuristicIframesOn: heuristicIframes
    };
  }

  async function applyState() {
    const state = await getState();
    siteActive = state.active;
    heuristicIframesOn = state.heuristicIframesOn;
    if (siteActive) {
      injectStyle();
      runScan();
      startObserving();
    } else {
      removeStyle();
      stopObserving();
    }
  }

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== 'local') return;
    if (changes.whitelist || changes.masterEnabled || changes.cosmeticFiltering || changes.heuristicIframes) {
      applyState();
    }
  });

  // Мост от scriptlets.js (MAIN world) — там нет доступа к chrome.* API,
  // поэтому событие долетает сюда как обычный DOM CustomEvent.
  document.addEventListener('__fb_defuse__', () => {
    chrome.runtime.sendMessage({ type: 'SCRIPTLET_DEFUSE_COUNT', count: 1 }).catch(() => {});
  });

  applyState();
})();
