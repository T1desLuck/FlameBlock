// fingerprint-protect.js — MAIN world. Малозаметная защита от Canvas/WebGL/
// Audio/шрифтового отпечатка браузера (browser fingerprinting).
//
// Ключевой принцип, важный по итогам изучения темы: наивная защита (много
// случайного шума на все точки подряд) детектируется антифрод-системами ещё
// легче, чем сам факт отсутствия защиты — резкий, крупный шум сам становится
// узнаваемым признаком "тут стоит anti-fingerprint расширение". Правильный
// подход (как у устоявшихся инструментов вроде Canvas Blocker) — маленький,
// ДЕТЕРМИНИРОВАННЫЙ шум на небольшую долю точек:
//   - детерминированный (не chrome.crypto/Math.random на каждый вызов) —
//     чтобы повторное считывание ОДНОГО И ТОГО ЖЕ canvas в рамках одной
//     загрузки страницы давало ОДИНАКОВЫЙ результат. Если значение будет
//     "плавать" от вызова к вызову — это тоже детектируется и выдаёт защиту.
//   - между разными загрузками страницы сид новый — отпечаток не становится
//     новым постоянным идентификатором взамен старого.
//
// Регистрируется/снимается из background.js по отдельной настройке —
// независимо от стелс-скриптлета (scriptlets.js), это разные функции.

(function () {
  if (window.__fbFingerprintProtected) return;
  window.__fbFingerprintProtected = true;

  // mulberry32 — простой быстрый детерминированный ГПСЧ. Сид — случайный,
  // но только один раз за загрузку страницы, дальше вся последовательность
  // повторяема в рамках этой же загрузки.
  let seed = (Math.random() * 4294967296) >>> 0;
  function rand() {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  // Часть детекторов защиты прямо проверяют .toString() подменённой функции
  // (нативные функции браузера возвращают "[native code]", у подмены —
  // текст самой функции). Маскируем под нативную, чтобы не выдавать себя
  // этим самым простым способом проверки.
  function markNative(fn, name) {
    try {
      fn.toString = () => `function ${name}() { [native code] }`;
    } catch (e) { /* noop */ }
    return fn;
  }

  const NOISE_RATE = 1 / 500; // доля точек, которые вообще трогаем
  const MAX_NOISY_PIXELS = 2000000; // защита от заметного торможения на огромных canvas

  function addCanvasNoise(imageData) {
    const data = imageData.data;
    const pixelCount = data.length / 4;
    if (pixelCount > MAX_NOISY_PIXELS) return imageData; // слишком крупный — не трогаем, это не похоже на отпечаток
    for (let i = 0; i < data.length; i += 4) {
      if (rand() < NOISE_RATE) {
        const ch = (rand() * 3) | 0;
        const idx = i + ch;
        data[idx] = Math.max(0, Math.min(255, data[idx] + (rand() < 0.5 ? -1 : 1)));
      }
    }
    return imageData;
  }

  // ---------------- Canvas 2D ----------------

  const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
  CanvasRenderingContext2D.prototype.getImageData = markNative(function (...args) {
    const imageData = origGetImageData.apply(this, args);
    try { return addCanvasNoise(imageData); } catch (e) { return imageData; }
  }, 'getImageData');

  function noisyClone(canvas) {
    const ctx = canvas.getContext('2d');
    if (!ctx || canvas.width <= 0 || canvas.height <= 0) return null;
    const imageData = origGetImageData.call(ctx, 0, 0, canvas.width, canvas.height);
    addCanvasNoise(imageData);
    const tmp = document.createElement('canvas');
    tmp.width = canvas.width;
    tmp.height = canvas.height;
    tmp.getContext('2d').putImageData(imageData, 0, 0);
    return tmp;
  }

  const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
  HTMLCanvasElement.prototype.toDataURL = markNative(function (...args) {
    try {
      const tmp = noisyClone(this);
      if (tmp) return origToDataURL.apply(tmp, args);
    } catch (e) { /* noop — откатываемся на оригинал ниже */ }
    return origToDataURL.apply(this, args);
  }, 'toDataURL');

  const origToBlob = HTMLCanvasElement.prototype.toBlob;
  HTMLCanvasElement.prototype.toBlob = markNative(function (callback, ...rest) {
    try {
      const tmp = noisyClone(this);
      if (tmp) return origToBlob.call(tmp, callback, ...rest);
    } catch (e) { /* noop */ }
    return origToBlob.call(this, callback, ...rest);
  }, 'toBlob');

  // measureText — частичная защита от шрифтового отпечатка: крошечный
  // детерминированный сдвиг ширины (доли процента, незаметно для вёрстки),
  // достаточный, чтобы сломать точное совпадение хэша. Это не полная защита
  // от перебора шрифтов, а точечная мера на самом частом векторе измерения.
  const origMeasureText = CanvasRenderingContext2D.prototype.measureText;
  CanvasRenderingContext2D.prototype.measureText = markNative(function (...args) {
    const metrics = origMeasureText.apply(this, args);
    try {
      const delta = (rand() - 0.5) * 0.02;
      Object.defineProperty(metrics, 'width', { value: metrics.width + delta, configurable: true });
    } catch (e) { /* некоторые движки не дают переопределить — не критично */ }
    return metrics;
  }, 'measureText');

  // ---------------- WebGL ----------------
  // 37445 = UNMASKED_VENDOR_WEBGL, 37446 = UNMASKED_RENDERER_WEBGL —
  // возвращаем общие, максимально распространённые значения вместо
  // конкретной модели видеокарты пользователя.
  function patchWebGL(proto) {
    if (!proto || proto.__fbPatched) return;
    proto.__fbPatched = true;
    const origGetParameter = proto.getParameter;
    proto.getParameter = markNative(function (param) {
      if (param === 37445) return 'Google Inc. (Generic)';
      if (param === 37446) return 'ANGLE (Generic, Generic Graphics, Direct3D11 vs_5_0 ps_5_0, D3D11)';
      return origGetParameter.call(this, param);
    }, 'getParameter');
  }
  if (window.WebGLRenderingContext) patchWebGL(WebGLRenderingContext.prototype);
  if (window.WebGL2RenderingContext) patchWebGL(WebGL2RenderingContext.prototype);

  // ---------------- AudioContext ----------------
  // Шум добавляется один раз на конкретный (buffer, channel) — не при
  // каждом обращении — иначе повторные считывания одного и того же буфера
  // накапливали бы шум и давали разные значения на разных вызовах, что само
  // по себе детектируется.
  const noisedAudioChannels = new WeakMap();
  function patchAudioBuffer(proto) {
    if (!proto) return;
    const origGetChannelData = proto.getChannelData;
    proto.getChannelData = markNative(function (channel) {
      const data = origGetChannelData.call(this, channel);
      let seen = noisedAudioChannels.get(this);
      if (!seen) { seen = new Set(); noisedAudioChannels.set(this, seen); }
      if (!seen.has(channel)) {
        seen.add(channel);
        for (let i = 0; i < data.length; i += 100) {
          data[i] = data[i] + (rand() - 0.5) * 0.0001;
        }
      }
      return data;
    }, 'getChannelData');
  }
  if (window.AudioBuffer) patchAudioBuffer(AudioBuffer.prototype);
})();
