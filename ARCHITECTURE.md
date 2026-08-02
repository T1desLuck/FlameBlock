<div align="center">

<a href="README.md">📘 README</a> · <a href="ARCHITECTURE.md"><b>📗 Техническая документация</b></a>

<br><br>

# Техническая документация FlameBlock

**Manifest V3 · Service Worker · MAIN/ISOLATED world · declarativeNetRequest**

</div>

---

## Оглавление

1. [Обзор архитектуры](#1-обзор-архитектуры)
2. [Manifest и разрешения](#2-manifest-и-разрешения)
3. [Структура файлов](#3-структура-файлов)
4. [Сетевая блокировка и система приоритетов правил](#4-сетевая-блокировка-и-система-приоритетов-правил)
5. [Подсчёт заблокированного и бейдж](#5-подсчёт-заблокированного-и-бейдж)
6. [Косметическая фильтрация (content.js)](#6-косметическая-фильтрация-contentjs)
7. [Эвристика по размеру iframe](#7-эвристика-по-размеру-iframe)
8. [Стелс-режим](#8-стелс-режим)
9. [Защита от отпечатка браузера (fingerprint-protect.js)](#9-защита-от-отпечатка-браузера-fingerprint-protectjs)
10. [Динамическая регистрация MAIN-world скриптов](#10-динамическая-регистрация-main-world-скриптов)
11. [Защита от утечки WebRTC](#11-защита-от-утечки-webrtc)
12. [Пользовательские правила](#12-пользовательские-правила)
13. [Хранение данных](#13-хранение-данных)
14. [Протокол сообщений](#14-протокол-сообщений)
15. [Локализация](#15-локализация)
16. [Известные ограничения](#16-известные-ограничения)

---

## 1. Обзор архитектуры

FlameBlock построен на Manifest V3 и состоит из четырёх исполняемых контекстов:

| Контекст | Файл | Мир (world) | Задача |
|---|---|---|---|
| Service worker | `background.js` | — | Сетевая блокировка (DNR), счётчики, синхронизация настроек, регистрация MAIN-world скриптов |
| Content script | `content.js` | ISOLATED | Косметическое скрытие рекламы, эвристика по iframe, доступ к `chrome.*` API |
| Инъекция в страницу | `fingerprint-protect.js` | MAIN | Патчинг `Canvas`/`WebGL`/`AudioBuffer` на уровне страницы |
| Инъекция в страницу | `scriptlets.js` | MAIN | Стелс-режим, гейт на `window.open` |

Главная причина разделения на ISOLATED и MAIN миры — ограничение платформы: у content-скриптов в ISOLATED world есть доступ к `chrome.*` API, но нет прямого доступа к нативным объектам страницы (перехват `CanvasRenderingContext2D.prototype` в изолированном мире не подействует на скрипты самой страницы). Поэтому патчинг API браузера обязан выполняться в MAIN world — но там, наоборот, нет `chrome.*` API. Мост между двумя мирами — `CustomEvent` на `document` (см. [§8](#8-стелс-режим)).

## 2. Manifest и разрешения

```json
{
  "manifest_version": 3,
  "version": "1.14.0",
  "default_locale": "ru",
  "minimum_chrome_version": "102",
  "permissions": [
    "declarativeNetRequest", "storage", "webRequest",
    "webNavigation", "tabs", "scripting", "favicon", "privacy"
  ],
  "host_permissions": ["<all_urls>"]
}
```

### Обоснование разрешений

| Разрешение | Зачем |
|---|---|
| `declarativeNetRequest` | Базовая блокировка рекламы/трекеров/антиадблока через статические `rule_resources` и динамические правила (вайт-лист, свои правила) |
| `storage` | `chrome.storage.local` — настройки, правила; `chrome.storage.session` — счётчики на вкладку (переживают перезапуск service worker) |
| `webRequest` | Только `onErrorOccurred` — считает `net::ERR_BLOCKED_BY_CLIENT`, чтобы показать пользователю число блокировок. Сам блок делает DNR, `webRequest` здесь не блокирует, а лишь наблюдает |
| `webNavigation` | `onBeforeNavigate` — сброс счётчиков вкладки при переходе на новую страницу (main frame) |
| `tabs` | Определение активной вкладки для попапа (`GET_SITE_INFO`) и инъекции MAIN-world скриптов в уже открытые вкладки |
| `scripting` | Регистрация/снятие MAIN-world скриптов (`registerContentScripts`) и точечная инъекция в открытые вкладки (`executeScript`) |
| `privacy` | `chrome.privacy.network.webRTCIPHandlingPolicy` — официальный API браузера для защиты от утечки WebRTC (см. [§11](#11-защита-от-утечки-webrtc)) |
| `favicon` | Отображение иконки сайта в интерфейсе попапа/настроек |
| `host_permissions: <all_urls>` | Реклама и трекеры размещаются на произвольных доменах; фиксированный список хостов сделал бы блокировку неполной |

## 3. Структура файлов

```
manifest.json
background.js               # service worker
common.js                     # общие хелперы: fbGetSettings/fbSetSettings, fbFormatCount,
                               # fbAllocateRuleId, fbGetHostname, fbHostnameInList, FB_BADGE_COLOR
content.js                     # ISOLATED world: косметика + iframe-эвристика
fingerprint-protect.js        # MAIN world: антифингерпринт
scriptlets.js                  # MAIN world: стелс-режим
i18n.js                         # локализация интерфейса popup/options
index.html                      # сайт проекта (GitHub Pages)
privacy.html                     # политика конфиденциальности (GitHub Pages)
robots.txt
sitemap.xml

icons/
├── icon16.png
├── icon32.png
├── icon48.png
└── icon128.png

image/
└── ICON.png                      # логотип/фавикон для сайта и README

popup/
├── popup.html                     # интерфейс попапа
├── popup.css
└── popup.js

options/
├── options.html                    # страница настроек
├── options.css
└── options.js

rules/
├── ads.json                         # статический DNR-набор: реклама
├── trackers.json                     # статический DNR-набор: трекеры
└── antiadblock.json                  # статический DNR-набор: антиадблок-скрипты

_locales/                              # 12 языков, __MSG_extName__ / __MSG_extDescription__
├── ru/messages.json
├── en/messages.json
├── de/messages.json
├── es/messages.json
├── fr/messages.json
├── hi/messages.json
├── id/messages.json
├── ja/messages.json
├── ko/messages.json
├── ar/messages.json
├── pt_BR/messages.json
└── zh_CN/messages.json
```

> `i18n.js` отвечает за локализацию текстов внутри интерфейса popup/options (не за строки самого манифеста — те резолвятся браузером автоматически из `_locales/<lang>/messages.json` через синтаксис `__MSG_key__`). Если понадобится расписать его логику подробнее — пришлите исходник, и в документацию добавится отдельный раздел, как для остальных модулей.

## 4. Сетевая блокировка и система приоритетов правил

Базовая блокировка — три статических `rule_resources`, подключённых в манифесте:

```json
"declarative_net_request": {
  "rule_resources": [
    { "id": "ads_ruleset", "enabled": true, "path": "rules/ads.json" },
    { "id": "trackers_ruleset", "enabled": true, "path": "rules/trackers.json" },
    { "id": "antiadblock_ruleset", "enabled": true, "path": "rules/antiadblock.json" }
  ]
}
```

Поверх них строятся **динамические** правила через `chrome.declarativeNetRequest.updateDynamicRules`, с системой приоритетов — чем выше число, тем правило "сильнее":

| Приоритет | Источник | Действие |
|---|---|---|
| 1 | Статические списки (`ads_ruleset`, `trackers_ruleset`, `antiadblock_ruleset`) | `block` |
| 2 | Вайт-лист сайта (`fbSetSiteEnabled`) | `allow`, условие `initiatorDomains: [hostname]` |
| 3 | Пользовательские правила (`fbSaveCustomRules`) | `block` или `allow`, условие `urlFilter: "||domain^"` |

Благодаря приоритету 3 собственное правило пользователя побеждает даже вайт-лист сайта: например, можно разрешить сайт целиком (приоритет 2), но явно заблокировать один поддомен своим правилом (приоритет 3).

Каждое динамическое правило получает `id` через `fbAllocateRuleId()` (в `common.js`) и распространяется на широкий набор `resourceTypes`: `main_frame`, `sub_frame`, `script`, `image`, `xmlhttprequest`, `media`, `font`, `object`, `ping`, `other`, `websocket`, `stylesheet`.

## 5. Подсчёт заблокированного и бейдж

DNR блокирует запросы сам, без участия JS — поэтому для отображения счётчика на бейдже расширения используется побочный эффект блокировки: подписка на `chrome.webRequest.onErrorOccurred` и фильтр по `details.error === 'net::ERR_BLOCKED_BY_CLIENT'`.

Счётчики хранятся **не** в обычной переменной service worker'а, а в `chrome.storage.session` — потому что service worker в MV3 может быть выгружен и перезапущен браузером в любой момент, и обычная переменная в памяти просто обнулится:

```js
tabCount_<tabId>              // общий счётчик блокировок на вкладке
iframeHeuristicCount_<tabId>  // отдельный счётчик именно iframe-эвристики
```

Отдельный счётчик для iframe-эвристики нужен, чтобы пользователь мог убедиться, что функция реально что-то ловит, не разбираясь в общем числе, где всё смешано со списками и CSS.

Жизненный цикл счётчиков:

- `webNavigation.onBeforeNavigate` (при `frameId === 0`, то есть переход именно в main frame) — сброс обоих счётчиков вкладки в 0.
- `tabs.onRemoved` — удаление ключей из `chrome.storage.session`, чтобы не копился мусор.
- При каждом инкременте бейдж обновляется через `chrome.action.setBadgeText` / `setBadgeBackgroundColor` / `setBadgeTextColor`, число форматируется `fbFormatCount()` (сокращение вида `1.1K`).
- Общий счётчик за всё время (`totalBlocked`) хранится отдельно в `chrome.storage.local` как часть настроек и показывается в попапе.

## 6. Косметическая фильтрация (content.js)

Работает в ISOLATED world, `run_at: document_start`, `all_frames: true`. Состоит из трёх независимых слоёв.

### 6.1. CSS-селекторы

Список селекторов известных рекламных движков и разметки (Google Ads/GPT, DoubleClick, Taboola, Outbrain, MGID, Яндекс.РТБ, а также баннеры cookie-consent — OneTrust, Cookiebot, Didomi, Usercentrics и т.д.) внедряется единым `<style>`-тегом с `display: none !important` — это дешевле по производительности, чем скрывать элементы поштучно через JS.

### 6.2. Текстовые метки

Регулярное выражение ищет короткие самостоятельные подписи вроде «Реклама», «Sponsored», «На правах рекламы» и скрывает контейнер на 1–2 уровня выше найденного узла — упрощённый аналог `:has-text()` + `:upward()` из uBlock Origin. Условия намеренно строгие (короткая длина текста, точное совпадение по regex, узел без дочерних элементов), чтобы не скрыть случайно статью, которая просто упоминает слово «реклама» в тексте.

### 6.3. Наблюдение за DOM

`MutationObserver` на `document.documentElement` (`childList + subtree`) с дебаунсом 400 мс (`scheduleScan`) — большинство SPA и рекламных виджетов подгружают контент асинхронно, разовой проверки при загрузке недостаточно.

Все три слоя управляются общим состоянием, читаемым из `chrome.storage.local` (`masterEnabled`, `cosmeticFiltering`, `heuristicIframes`, `whitelist`) и реагирующим на `chrome.storage.onChanged` в реальном времени, без перезагрузки страницы.

## 7. Эвристика по размеру iframe

Выключена по умолчанию — задумана специально для случая, когда сайт проксирует рекламу через собственный домен, и внешние списки блокировки её не видят в принципе (нет стороннего домена, который можно было бы занести в список).

Алгоритм:

1. Для каждого `<iframe>` определяется размер — сперва атрибуты `width`/`height`, затем `getComputedStyle`, затем `offsetWidth/offsetHeight` (фреймы иногда ещё не отрисованы к моменту первого прохода — статус `{tries, done}` хранится в `WeakMap`, до 6 повторных попыток с интервалом 700 мс).
2. Размер сверяется со списком стандартных рекламных форматов (IAB-подобные размеры: `300×250`, `728×90`, `320×50`, `160×600`, `970×250` и другие — всего 20 размеров) с допуском ±2 пикселя.
3. Если фрейм с чужого домена **и** совпадает по размеру — скрывается сразу.
4. Если фрейм со своего домена (тот самый случай прокси-рекламы, ради которого функция и создавалась) — требуется дополнительное подтверждение: `id`, `class` или `src` самого фрейма или одного из двух его родителей должны содержать явный рекламный признак (`ad`, `ads`, `advert`, `banner`, `sponsor`, `promo`, `dfp`, `gpt`, `zone`). Это защищает от случайного скрытия легитимного виджета того же размера.

Результат репортится в background через сообщение `IFRAME_HEURISTIC_COUNT`.

## 8. Стелс-режим

Реализован в `scriptlets.js` (MAIN world). Блокирует известные скрипты обнаружения блокировщика на сетевом уровне (через тот же DNR-список `antiadblock_ruleset`) и дополнительно ставит гейт на `window.open`, чтобы гасить попандеры и принудительные редиректы прямо на странице.

Поскольку MAIN world не имеет доступа к `chrome.*` API, о сработавшей защите он сообщает через `CustomEvent` на `document`:

```js
document.dispatchEvent(new CustomEvent('__fb_defuse__'));
```

`content.js` (ISOLATED world) слушает это событие и пересылает его в background как обычное сообщение `SCRIPTLET_DEFUSE_COUNT` — так замыкается мост между мирами.

## 9. Защита от отпечатка браузера (fingerprint-protect.js)

MAIN world, патчит нативные API непосредственно в контексте страницы.

### 9.1. Ключевой принцип: детерминированный, а не случайный шум

Наивная защита — случайный шум на каждый вызов — детектируется антифрод-системами легче, чем полное отсутствие защиты: сам факт того, что значение "плавает" от вызова к вызову, — узнаваемый признак работы anti-fingerprint расширения. Правильный подход (как у устоявшихся инструментов вроде Canvas Blocker):

- **Детерминированный** ГПСЧ (`mulberry32`), а не `Math.random()` на каждый вызов — повторное считывание одного и того же canvas в рамках одной загрузки страницы даёт одинаковый результат.
- Сид **новый на каждую загрузку страницы** — отпечаток не превращается в новый постоянный идентификатор взамен старого.
- Шум применяется к небольшой доле точек (`NOISE_RATE = 1/500`), а не ко всем подряд.

### 9.2. Маскировка под нативный код

Часть детекторов проверяет `Function.prototype.toString()` подменённой функции (у настоящей нативной функции — `"[native code]"`, у подмены — текст самой функции). `markNative()` переопределяет `toString`, чтобы патч не выдавал себя этим способом.

### 9.3. Что патчится

| API | Метод защиты |
|---|---|
| `CanvasRenderingContext2D.getImageData` | Шум добавляется прямо в `ImageData` перед возвратом |
| `HTMLCanvasElement.toDataURL` / `toBlob` | Canvas клонируется во временный `<canvas>` с уже зашумлёнными пикселями (`noisyClone`), оригинал не трогается — вызов идёт на клоне |
| `CanvasRenderingContext2D.measureText` | Крошечный детерминированный сдвиг `width` (доли процента) — ломает точное совпадение хэша шрифтового отпечатка, не влияя на вёрстку |
| `WebGLRenderingContext` / `WebGL2RenderingContext.getParameter` | Для `UNMASKED_VENDOR_WEBGL` (37445) и `UNMASKED_RENDERER_WEBGL` (37446) возвращаются общие, максимально распространённые значения вместо модели конкретной видеокарты |
| `AudioBuffer.getChannelData` | Разреженный шум (каждый 100-й семпл, амплитуда 0.0001) добавляется **один раз** на конкретную пару `(buffer, channel)` — отслеживается через `WeakMap<AudioBuffer, Set<channel>>`, чтобы повторные считывания не накапливали шум и не давали разных значений при разных вызовах (что тоже детектируется) |

Для больших canvas (`> MAX_NOISY_PIXELS = 2,000,000` точек) шум не применяется — заметное торможение на таком объёме было бы более узнаваемым признаком, чем отсутствие защиты.

## 10. Динамическая регистрация MAIN-world скриптов

`fingerprint-protect.js` и `scriptlets.js` — независимые функции с раздельными настройками (`fingerprintProtection`, `stealthMode`), регистрируются в браузере по отдельности через `chrome.scripting.registerContentScripts` / `unregisterContentScripts`, с `runAt: 'document_start'`, `world: 'MAIN'`, `allFrames: true`.

Важный нюанс платформы: свежая регистрация MAIN-world скрипта распространяется только на **следующие** загрузки страниц — уже открытые вкладки её не подхватывают сами по себе. Чтобы включение защиты действовало немедленно, без ручной перезагрузки вкладок, `fbInjectIntoOpenTabs()` дополнительно инъецирует файл напрямую во все уже открытые вкладки через `chrome.scripting.executeScript({ world: 'MAIN' })`.

## 11. Защита от утечки WebRTC

Реализована не JS-перехватом на странице, а официальной настройкой браузера — `chrome.privacy.network.webRTCIPHandlingPolicy`, что надёжнее любого перехвата в скрипте:

```js
policy = enabled ? 'disable_non_proxied_udp' : 'default';
chrome.privacy.network.webRTCIPHandlingPolicy.set({ value: policy });
```

Выключено по умолчанию: полное экранирование ломает видеозвонки прямо в браузере (Google Meet и подобные) на сайтах, которые не умеют работать через прокси-соединение — включение оставлено на осознанный выбор пользователя.

## 12. Пользовательские правила

Синтаксис в духе Adblock/uBlock, одно правило на строку:

| Синтаксис | Значение |
|---|---|
| `domain.com` | Блокировать домен |
| `@@domain.com` | Явно разрешить (перекрывает блокировку) |
| `! комментарий` или `# комментарий` | Игнорируется |
| `\|\|domain.com^` | ABP-синтаксис — `\|\|` и `^` автоматически отбрасываются при разборе |

Парсинг (`fbParseCustomLine`) валидирует домен регулярным выражением (`[a-zA-Z0-9.\-]+`), после чего каждое правило превращается в динамическое DNR-правило с `priority: 3` (см. [§4](#4-сетевая-блокировка-и-система-приоритетов-правил)) и `urlFilter: "||domain^"`. При сохранении старые правила пользователя полностью удаляются (`removeRuleIds`) и заменяются новыми — списк хранится как `customRules: [{ ruleId, type, text }]`.

## 13. Хранение данных

| Хранилище | Время жизни | Что хранится |
|---|---|---|
| `chrome.storage.local` | Постоянно, до удаления расширения | `masterEnabled`, `adBlocking`, `trackerBlocking`, `stealthMode`, `cosmeticFiltering`, `heuristicIframes`, `fingerprintProtection`, `webrtcProtection`, `whitelist`, `whitelistRuleIds`, `customRules`, `totalBlocked`, `installDate`, язык интерфейса |
| `chrome.storage.session` | До закрытия браузера, переживает перезапуск service worker | `tabCount_<tabId>`, `iframeHeuristicCount_<tabId>` |

Ничего из перечисленного не покидает устройство пользователя — оба типа хранилища локальные API самого браузера.

## 14. Протокол сообщений

Все сообщения идут через `chrome.runtime.onMessage`, обрабатываются асинхронно (`return true` в листенере background.js):

| Тип сообщения | Отправитель | Что делает |
|---|---|---|
| `GET_SITE_INFO` | popup | Возвращает хостname, статус защиты, счётчики для текущей вкладки |
| `SET_SITE_ENABLED` | popup | Добавляет/убирает сайт из вайт-листа (динамическое DNR-правило приоритета 2) |
| `SET_MASTER_ENABLED` | popup | Общий выключатель, синхронизирует MAIN-world скрипты |
| `GET_SETTINGS` / `SET_SETTINGS` | options/popup | Чтение/запись всех настроек, с последующей синхронизацией скриптов |
| `SAVE_CUSTOM_RULES` | options | Пересборка динамических DNR-правил из текстового поля |
| `REMOVE_FROM_WHITELIST` | popup/options | Явное снятие сайта с вайт-листа |
| `COSMETIC_HIDE_COUNT` | content.js | Инкремент счётчика от CSS/текстового слоя фильтрации |
| `IFRAME_HEURISTIC_COUNT` | content.js | Инкремент общего счётчика **и** отдельного счётчика iframe-эвристики |
| `SCRIPTLET_DEFUSE_COUNT` | content.js (мост от scriptlets.js) | Инкремент счётчика от сработавшего стелс-режима |

## 15. Локализация

`default_locale: "ru"`, строки вида `__MSG_extName__` разрешаются из `_locales/<lang>/messages.json`. Поддерживается 12 языков: ru, en, zh_CN, es, hi, ar, pt_BR, ja, ko, de, fr, id. Определение языка — по умолчанию автоматическое (`navigator.language` / язык браузера), с возможностью ручного переопределения в настройках, которое сохраняется в `chrome.storage.local`.

## 16. Известные ограничения

- **Эвристика по размеру iframe** может изредка скрыть легитимный виджет стандартного рекламного размера — поэтому выключена по умолчанию и требует дополнительного признака (`hasAdHint`) для фреймов со своего домена.
- **Защита от утечки WebRTC** может мешать видеозвонкам в браузере на сайтах, не поддерживающих корректную маршрутизацию через прокси — выключена по умолчанию.
- **Защита от отпечатка браузера** — точечная мера на самых частых векторах измерения (Canvas, WebGL, Audio, шрифты), а не полная защита от всех существующих техник fingerprinting.
- Счётчик блокировок опирается на `webRequest.onErrorOccurred` и отражает именно `net::ERR_BLOCKED_BY_CLIENT` — используется только для отображения числа пользователю, не для самой блокировки (её выполняет DNR).

---

<div align="center">

<a href="README.md">📘 README</a> · <a href="ARCHITECTURE.md"><b>📗 Техническая документация</b></a>

</div>
