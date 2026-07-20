// scriptlets.js — запускается в MAIN world (контекст самой страницы, а не
// изолированный мир расширения). Поэтому у него НЕТ доступа к chrome.* API —
// это ограничение самой платформы Manifest V3, а не наш недосмотр. Общаемся
// с content.js через CustomEvent на document, который изолированный мир видит.
//
// Регистрируется/снимается из background.js в зависимости от стелс-режима —
// сам скрипт не читает настройки, поэтому остаётся маленьким и статичным
// (что и требует MV3 — никакого eval/динамического кода).

(function () {
  if (window.__fbScriptletsInjected) return;
  window.__fbScriptletsInjected = true;

  const GESTURE_WINDOW_MS = 1200;
  let lastGestureAt = 0;

  function markGesture(e) {
    if (e.isTrusted) lastGestureAt = Date.now();
  }
  ['click', 'mousedown', 'keydown', 'touchstart'].forEach((evt) => {
    window.addEventListener(evt, markGesture, { capture: true, passive: true });
  });

  function reportDefuse() {
    try {
      document.dispatchEvent(new CustomEvent('__fb_defuse__'));
    } catch (e) { /* noop */ }
  }

  // Гейт на window.open: попандеры/принудительные редиректы открывают новое
  // окно без настоящего клика пользователя — реальные "открыть в новой
  // вкладке" почти всегда происходят в первую секунду после клика/нажатия.
  const nativeOpen = window.open;
  window.open = function (...args) {
    const sinceGesture = Date.now() - lastGestureAt;
    if (sinceGesture > GESTURE_WINDOW_MS) {
      reportDefuse();
      return null;
    }
    return nativeOpen.apply(window, args);
  };
})();
