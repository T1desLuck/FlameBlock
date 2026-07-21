#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор _locales/<код>/messages.json для всех 12 языков FlameBlock.

Единый источник правды — словарь TRANSLATIONS ниже: ключ -> {локаль: текст}.
Скрипт СТРОГО проверяет, что у каждого ключа есть перевод на ВСЕ 12 языков —
если чего-то не хватает, скрипт падает с ошибкой вместо того, чтобы молча
сгенерировать неполную локализацию. Это и есть механизм "не упустить ничего".
"""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
LOCALES = ['ru', 'en', 'zh_CN', 'es', 'hi', 'ar', 'pt_BR', 'ja', 'ko', 'de', 'fr', 'id']

TRANSLATIONS = {
    "extName": {
        "ru": "FlameBlock — блокировщик рекламы",
        "en": "FlameBlock — Ad Blocker",
        "zh_CN": "FlameBlock — 广告拦截器",
        "es": "FlameBlock — Bloqueador de anuncios",
        "hi": "FlameBlock — विज्ञापन अवरोधक",
        "ar": "FlameBlock — حاجب الإعلانات",
        "pt_BR": "FlameBlock — Bloqueador de anúncios",
        "ja": "FlameBlock — 広告ブロッカー",
        "ko": "FlameBlock — 광고 차단기",
        "de": "FlameBlock — Werbeblocker",
        "fr": "FlameBlock — Bloqueur de publicités",
        "id": "FlameBlock — Pemblokir Iklan",
    },
    "extDescription": {
        "ru": "Продвинутый блокировщик рекламы и трекеров. Работает локально — данные никуда не отправляются и не собираются.",
        "en": "Advanced ad & tracker blocker. Fully local — no data is ever collected or sent anywhere.",
        "zh_CN": "先进的广告与跟踪器拦截器,完全本地运行,不收集也不发送任何数据。",
        "es": "Bloqueador avanzado de anuncios y rastreadores. Funciona 100% en local: no se recopila ni envía ningún dato.",
        "hi": "विज्ञापन और ट्रैकर के लिए एडवांस्ड ब्लॉकर। पूरी तरह लोकल — कोई डेटा एकत्र या कहीं नहीं भेजा जाता।",
        "ar": "حاجب إعلانات ومتتبعات متقدم. يعمل محليًا بالكامل — لا تُجمع أو تُرسل أي بيانات إلى أي جهة.",
        "pt_BR": "Bloqueador avançado de anúncios e rastreadores. 100% local — nenhum dado é coletado ou enviado.",
        "ja": "広告・トラッカーを高度にブロック。完全ローカル動作でデータの収集・送信は一切ありません。",
        "ko": "광고 및 트래커 차단기. 완전히 로컬에서 동작하며 데이터를 수집하거나 전송하지 않습니다.",
        "de": "Fortschrittlicher Werbe- und Tracker-Blocker. Läuft komplett lokal — es werden keine Daten gesammelt oder gesendet.",
        "fr": "Bloqueur avancé de publicités et traqueurs. Fonctionne 100% en local — aucune donnée collectée ni envoyée.",
        "id": "Pemblokir iklan & pelacak tingkat lanjut. Bekerja 100% lokal — tidak ada data yang dikumpulkan atau dikirim.",
    },
    "pause_all_title": {
        "ru": "Приостановить везде", "en": "Pause everywhere", "zh_CN": "在所有网站暂停",
        "es": "Pausar en todas partes", "hi": "हर जगह रोकें", "ar": "إيقاف مؤقت في كل مكان",
        "pt_BR": "Pausar em todos os sites", "ja": "すべてのサイトで一時停止", "ko": "모든 사이트에서 일시중지",
        "de": "Überall pausieren", "fr": "Suspendre partout", "id": "Jeda di semua situs",
    },
    "resume_protection_title": {
        "ru": "Возобновить защиту", "en": "Resume protection", "zh_CN": "恢复防护",
        "es": "Reanudar la protección", "hi": "सुरक्षा फिर से शुरू करें", "ar": "استئناف الحماية",
        "pt_BR": "Retomar a proteção", "ja": "保護を再開", "ko": "보호 다시 시작",
        "de": "Schutz fortsetzen", "fr": "Reprendre la protection", "id": "Lanjutkan perlindungan",
    },
    "this_site": {
        "ru": "Этот сайт", "en": "This site", "zh_CN": "当前网站",
        "es": "Este sitio", "hi": "यह साइट", "ar": "هذا الموقع",
        "pt_BR": "Este site", "ja": "このサイト", "ko": "이 사이트",
        "de": "Diese Website", "fr": "Ce site", "id": "Situs ini",
    },
    "protection_on": {
        "ru": "Защита включена", "en": "Protection is on", "zh_CN": "防护已开启",
        "es": "Protección activada", "hi": "सुरक्षा चालू है", "ar": "الحماية مفعّلة",
        "pt_BR": "Proteção ativada", "ja": "保護は有効です", "ko": "보호 기능 켜짐",
        "de": "Schutz ist aktiv", "fr": "Protection activée", "id": "Perlindungan aktif",
    },
    "ads_allowed_here": {
        "ru": "Реклама разрешена на этом сайте", "en": "Ads are allowed on this site",
        "zh_CN": "该网站已允许显示广告", "es": "Los anuncios están permitidos en este sitio",
        "hi": "इस साइट पर विज्ञापनों की अनुमति है", "ar": "الإعلانات مسموح بها في هذا الموقع",
        "pt_BR": "Anúncios permitidos neste site", "ja": "このサイトでは広告が許可されています",
        "ko": "이 사이트에서는 광고가 허용됩니다", "de": "Werbung ist auf dieser Website erlaubt",
        "fr": "Les publicités sont autorisées sur ce site", "id": "Iklan diizinkan di situs ini",
    },
    "on_page": {
        "ru": "на странице", "en": "on this page", "zh_CN": "本页",
        "es": "en esta página", "hi": "इस पेज पर", "ar": "في هذه الصفحة",
        "pt_BR": "nesta página", "ja": "このページで", "ko": "이 페이지",
        "de": "auf dieser Seite", "fr": "sur cette page", "id": "di halaman ini",
    },
    "total_blocked_label": {
        "ru": "всего заблокировано", "en": "total blocked", "zh_CN": "累计拦截",
        "es": "bloqueados en total", "hi": "कुल ब्लॉक किए गए", "ar": "إجمالي المحظور",
        "pt_BR": "total bloqueado", "ja": "累計ブロック数", "ko": "총 차단 수",
        "de": "insgesamt blockiert", "fr": "total bloqué", "id": "total diblokir",
    },
    "reload_page": {
        "ru": "Обновить страницу", "en": "Reload page", "zh_CN": "刷新页面",
        "es": "Actualizar página", "hi": "पेज रीलोड करें", "ar": "إعادة تحميل الصفحة",
        "pt_BR": "Recarregar página", "ja": "ページを再読み込み", "ko": "페이지 새로고침",
        "de": "Seite neu laden", "fr": "Actualiser la page", "id": "Muat ulang halaman",
    },
    "extension_settings": {
        "ru": "Настройки расширения", "en": "Extension settings", "zh_CN": "扩展程序设置",
        "es": "Configuración de la extensión", "hi": "एक्सटेंशन सेटिंग्स", "ar": "إعدادات الإضافة",
        "pt_BR": "Configurações da extensão", "ja": "拡張機能の設定", "ko": "확장 프로그램 설정",
        "de": "Erweiterungseinstellungen", "fr": "Paramètres de l'extension", "id": "Pengaturan ekstensi",
    },
    "options_subtitle": {
        "ru": "Продвинутые настройки расширения", "en": "Advanced extension settings",
        "zh_CN": "扩展程序高级设置", "es": "Configuración avanzada de la extensión",
        "hi": "एक्सटेंशन की एडवांस्ड सेटिंग्स", "ar": "الإعدادات المتقدمة للإضافة",
        "pt_BR": "Configurações avançadas da extensão", "ja": "拡張機能の詳細設定", "ko": "확장 프로그램 고급 설정",
        "de": "Erweiterte Einstellungen der Erweiterung", "fr": "Paramètres avancés de l'extension",
        "id": "Pengaturan lanjutan ekstensi",
    },
    "section_language": {
        "ru": "Язык", "en": "Language", "zh_CN": "语言",
        "es": "Idioma", "hi": "भाषा", "ar": "اللغة",
        "pt_BR": "Idioma", "ja": "言語", "ko": "언어",
        "de": "Sprache", "fr": "Langue", "id": "Bahasa",
    },
    "language_hint": {
        "ru": "Определяется автоматически по языку браузера. Можно выбрать вручную — выбор запомнится.",
        "en": "Detected automatically from your browser's language. You can also pick one manually — your choice is remembered.",
        "zh_CN": "默认根据浏览器语言自动检测,也可以手动选择,系统会记住您的选择。",
        "es": "Se detecta automáticamente según el idioma del navegador. También puedes elegirlo manualmente: la elección se recordará.",
        "hi": "यह आपके ब्राउज़र की भाषा से अपने आप तय होती है। आप इसे मैन्युअल रूप से भी चुन सकते हैं — आपकी पसंद याद रखी जाएगी।",
        "ar": "تُحدَّد تلقائيًا حسب لغة المتصفح. يمكنك أيضًا اختيارها يدويًا — وسيُحفظ اختيارك.",
        "pt_BR": "Detectado automaticamente a partir do idioma do navegador. Você também pode escolher manualmente — a escolha será lembrada.",
        "ja": "通常はブラウザの言語から自動的に判定されます。手動で選ぶこともでき、その場合は選択内容が保存されます。",
        "ko": "기본적으로 브라우저 언어에 따라 자동으로 감지됩니다. 직접 선택할 수도 있으며, 선택한 언어는 저장됩니다.",
        "de": "Wird automatisch anhand der Sprache deines Browsers erkannt. Du kannst die Sprache auch manuell wählen — die Auswahl wird gespeichert.",
        "fr": "Détectée automatiquement selon la langue du navigateur. Vous pouvez aussi la choisir manuellement — votre choix sera mémorisé.",
        "id": "Terdeteksi otomatis dari bahasa browser Anda. Anda juga bisa memilihnya secara manual — pilihan akan diingat.",
    },
    "language_auto": {
        "ru": "Авто (по умолчанию)", "en": "Auto (default)", "zh_CN": "自动(默认)",
        "es": "Automático (predeterminado)", "hi": "ऑटो (डिफ़ॉल्ट)", "ar": "تلقائي (افتراضي)",
        "pt_BR": "Automático (padrão)", "ja": "自動(デフォルト)", "ko": "자동(기본값)",
        "de": "Automatisch (Standard)", "fr": "Automatique (par défaut)", "id": "Otomatis (default)",
    },
    "section_main_settings": {
        "ru": "Основные настройки", "en": "Main settings", "zh_CN": "基本设置",
        "es": "Configuración principal", "hi": "मुख्य सेटिंग्स", "ar": "الإعدادات الرئيسية",
        "pt_BR": "Configurações principais", "ja": "基本設定", "ko": "기본 설정",
        "de": "Grundeinstellungen", "fr": "Paramètres principaux", "id": "Pengaturan utama",
    },
    "master_enabled_title": {
        "ru": "Расширение включено", "en": "Extension enabled", "zh_CN": "扩展程序已启用",
        "es": "Extensión activada", "hi": "एक्सटेंशन चालू है", "ar": "الإضافة مفعّلة",
        "pt_BR": "Extensão ativada", "ja": "拡張機能を有効化", "ko": "확장 프로그램 사용",
        "de": "Erweiterung aktiviert", "fr": "Extension activée", "id": "Ekstensi diaktifkan",
    },
    "master_enabled_hint": {
        "ru": "Общий выключатель. Выключите, чтобы временно отключить FlameBlock везде.",
        "en": "Master switch. Turn it off to temporarily disable FlameBlock everywhere.",
        "zh_CN": "总开关。关闭后会在所有网站临时停用 FlameBlock。",
        "es": "Interruptor general. Desactívalo para desactivar FlameBlock temporalmente en todas partes.",
        "hi": "मुख्य स्विच। इसे बंद करने पर FlameBlock हर जगह अस्थायी रूप से बंद हो जाएगा।",
        "ar": "المفتاح الرئيسي. أوقفه لتعطيل FlameBlock مؤقتًا في كل مكان.",
        "pt_BR": "Interruptor geral. Desative para desligar o FlameBlock temporariamente em todos os sites.",
        "ja": "全体のオン/オフスイッチです。オフにすると、すべてのサイトでFlameBlockが一時的に無効になります。",
        "ko": "전체 스위치입니다. 끄면 모든 사이트에서 FlameBlock이 일시적으로 비활성화됩니다.",
        "de": "Hauptschalter. Schalte ihn aus, um FlameBlock vorübergehend überall zu deaktivieren.",
        "fr": "Interrupteur général. Désactivez-le pour désactiver temporairement FlameBlock partout.",
        "id": "Sakelar utama. Matikan untuk menonaktifkan FlameBlock sementara di semua situs.",
    },
    "block_ads_title": {
        "ru": "Блокировка рекламы", "en": "Ad blocking", "zh_CN": "广告拦截",
        "es": "Bloqueo de anuncios", "hi": "विज्ञापन ब्लॉकिंग", "ar": "حظر الإعلانات",
        "pt_BR": "Bloqueio de anúncios", "ja": "広告のブロック", "ko": "광고 차단",
        "de": "Werbeblockierung", "fr": "Blocage des publicités", "id": "Pemblokiran iklan",
    },
    "block_ads_hint": {
        "ru": "Сетевая блокировка запросов к известным рекламным сетям.",
        "en": "Network-level blocking of requests to known ad networks.",
        "zh_CN": "在网络层拦截对已知广告网络的请求。",
        "es": "Bloqueo a nivel de red de las solicitudes a redes publicitarias conocidas.",
        "hi": "जानी-मानी विज्ञापन नेटवर्क को होने वाले रिक्वेस्ट को नेटवर्क स्तर पर ब्लॉक करता है।",
        "ar": "حظر على مستوى الشبكة للطلبات الموجّهة إلى شبكات إعلانية معروفة.",
        "pt_BR": "Bloqueio em nível de rede de solicitações para redes de anúncios conhecidas.",
        "ja": "既知の広告ネットワークへのリクエストをネットワークレベルでブロックします。",
        "ko": "알려진 광고 네트워크로 향하는 요청을 네트워크 수준에서 차단합니다。".replace("。", "."),
        "de": "Blockiert Anfragen an bekannte Werbenetzwerke auf Netzwerkebene.",
        "fr": "Blocage au niveau réseau des requêtes vers des régies publicitaires connues.",
        "id": "Memblokir permintaan ke jaringan iklan yang dikenal di tingkat jaringan.",
    },
    "block_trackers_title": {
        "ru": "Блокировка трекеров", "en": "Tracker blocking", "zh_CN": "跟踪器拦截",
        "es": "Bloqueo de rastreadores", "hi": "ट्रैकर ब्लॉकिंग", "ar": "حظر المتتبعات",
        "pt_BR": "Bloqueio de rastreadores", "ja": "トラッカーのブロック", "ko": "트래커 차단",
        "de": "Tracker-Blockierung", "fr": "Blocage des traqueurs", "id": "Pemblokiran pelacak",
    },
    "block_trackers_hint": {
        "ru": "Блокирует счётчики и скрипты слежения за поведением на сайтах.",
        "en": "Blocks analytics counters and behavior-tracking scripts on websites.",
        "zh_CN": "拦截网站上的统计计数器和行为跟踪脚本。",
        "es": "Bloquea los contadores analíticos y los scripts que rastrean el comportamiento en los sitios web.",
        "hi": "वेबसाइटों पर मौजूद एनालिटिक्स काउंटर और व्यवहार-ट्रैकिंग स्क्रिप्ट को ब्लॉक करता है।",
        "ar": "يحظر عدّادات التحليلات وسكريبتات تتبع السلوك على المواقع.",
        "pt_BR": "Bloqueia contadores de análise e scripts de rastreamento de comportamento nos sites.",
        "ja": "サイト上のアクセス解析カウンターや行動追跡スクリプトをブロックします。",
        "ko": "웹사이트의 분석 카운터와 행동 추적 스크립트를 차단합니다.",
        "de": "Blockiert Analyse-Zähler und Skripte zur Verhaltensverfolgung auf Websites.",
        "fr": "Bloque les compteurs analytiques et les scripts de suivi du comportement sur les sites.",
        "id": "Memblokir penghitung analitik dan skrip pelacakan perilaku di situs web.",
    },
    "stealth_mode_title": {
        "ru": "Стелс-режим", "en": "Stealth mode", "zh_CN": "隐身模式",
        "es": "Modo sigiloso", "hi": "स्टेल्थ मोड", "ar": "وضع التخفي",
        "pt_BR": "Modo furtivo", "ja": "ステルスモード", "ko": "스텔스 모드",
        "de": "Stealth-Modus", "fr": "Mode furtif", "id": "Mode siluman",
    },
    "stealth_mode_hint": {
        "ru": "Блокирует известные анти-adblock скрипты сетевым способом и встраивает лёгкий скриптлет прямо в страницу (гейт на window.open против попандеров/принудительных редиректов). Список сервисов обновляется — не разовое и не вечное решение.",
        "en": "Blocks known anti-adblock scripts at the network level and injects a lightweight scriptlet directly into the page (a gate on window.open against pop-unders and forced redirects). The service list gets updated over time — it's not a one-time or permanent fix.",
        "zh_CN": "在网络层拦截已知的反广告拦截脚本,并直接向页面注入一个轻量脚本(对 window.open 设置门槛,拦截弹出式广告和强制跳转)。该服务列表会持续更新——这不是一次性或永久性的解决方案。",
        "es": "Bloquea a nivel de red los scripts anti-adblock conocidos e inyecta un scriptlet ligero directamente en la página (un control sobre window.open contra popunders y redirecciones forzadas). La lista de servicios se actualiza con el tiempo — no es una solución única ni permanente.",
        "hi": "जानी-मानी एंटी-एडब्लॉक स्क्रिप्ट को नेटवर्क स्तर पर ब्लॉक करता है और पेज में सीधे एक हल्का स्क्रिप्टलेट डालता है (पॉप-अंडर और ज़बरदस्ती रीडायरेक्ट के खिलाफ़ window.open पर गेट)। सेवाओं की सूची समय-समय पर अपडेट होती है — यह एक बार का या स्थायी समाधान नहीं है।",
        "ar": "يحظر سكريبتات كشف حاجبات الإعلانات المعروفة على مستوى الشبكة، ويُدرج سكريبتًا خفيفًا مباشرة في الصفحة (بوابة على window.open ضد النوافذ المنبثقة الخلفية وإعادة التوجيه القسري). تُحدَّث قائمة الخدمات بمرور الوقت — فهذا ليس حلًا نهائيًا أو دائمًا.",
        "pt_BR": "Bloqueia scripts anti-adblock conhecidos em nível de rede e injeta um scriptlet leve diretamente na página (um controle sobre window.open contra popunders e redirecionamentos forçados). A lista de serviços é atualizada com o tempo — não é uma solução única nem permanente.",
        "ja": "既知の広告ブロック検出スクリプトをネットワークレベルでブロックし、さらに軽量なスクリプトをページに直接挿入します(ポップアンダーや強制リダイレクトを防ぐためwindow.openにゲートをかけます)。対象サービスの一覧は随時更新されるもので、一度きりでも永久的な解決策でもありません。",
        "ko": "알려진 광고 차단 감지 스크립트를 네트워크 수준에서 차단하고, 페이지에 가벼운 스크립틀릿을 직접 삽입합니다(팝언더와 강제 리디렉션을 막기 위해 window.open에 게이트를 겁니다). 대상 서비스 목록은 계속 업데이트되며, 한 번으로 끝나거나 영구적인 해결책은 아닙니다.",
        "de": "Blockiert bekannte Anti-Adblock-Skripte auf Netzwerkebene und injiziert ein leichtgewichtiges Scriptlet direkt in die Seite (eine Sperre für window.open gegen Popunder und erzwungene Weiterleitungen). Die Liste der Dienste wird laufend aktualisiert — das ist keine einmalige oder dauerhafte Lösung.",
        "fr": "Bloque au niveau réseau les scripts anti-adblock connus et injecte un scriptlet léger directement dans la page (un verrou sur window.open contre les popunders et les redirections forcées). La liste des services évolue dans le temps — ce n'est ni une solution ponctuelle, ni définitive.",
        "id": "Memblokir skrip anti-adblock yang dikenal di tingkat jaringan dan menyisipkan scriptlet ringan langsung ke halaman (gerbang pada window.open melawan popunder dan pengalihan paksa). Daftar layanan terus diperbarui — ini bukan solusi sekali pakai atau permanen.",
    },
    "cosmetic_filtering_title": {
        "ru": "Косметическая фильтрация", "en": "Cosmetic filtering", "zh_CN": "外观过滤",
        "es": "Filtrado cosmético", "hi": "कॉस्मेटिक फ़िल्टरिंग", "ar": "الفلترة التجميلية",
        "pt_BR": "Filtragem cosmética", "ja": "コスメティックフィルタリング", "ko": "코스메틱 필터링",
        "de": "Kosmetische Filterung", "fr": "Filtrage cosmétique", "id": "Pemfilteran kosmetik",
    },
    "cosmetic_filtering_hint": {
        "ru": "Скрывает рекламные блоки на странице по CSS-паттернам и по коротким меткам вроде «Реклама»/«Sponsored», даже если это не отдельный сетевой запрос.",
        "en": "Hides ad blocks on the page by CSS patterns and by short labels like \"Ad\"/\"Sponsored\", even when it isn't a separate network request.",
        "zh_CN": "根据 CSS 特征以及\"广告\"/\"赞助内容\"之类的简短标签隐藏页面上的广告区块,即便它并非独立的网络请求。",
        "es": "Oculta los bloques publicitarios de la página según patrones CSS y etiquetas cortas como «Anuncio»/«Patrocinado», incluso cuando no se trata de una solicitud de red independiente.",
        "hi": "पेज पर मौजूद विज्ञापन ब्लॉक को CSS पैटर्न और \"विज्ञापन\"/\"प्रायोजित\" जैसे छोटे लेबल के आधार पर छुपाता है, भले ही यह अलग नेटवर्क रिक्वेस्ट न हो।",
        "ar": "يُخفي الكتل الإعلانية في الصفحة اعتمادًا على أنماط CSS وعلى تسميات قصيرة مثل «إعلان»/«برعاية»، حتى لو لم يكن الأمر طلب شبكة منفصلًا.",
        "pt_BR": "Oculta blocos de anúncios na página com base em padrões CSS e em rótulos curtos como \"Anúncio\"/\"Patrocinado\", mesmo quando isso não é uma solicitação de rede separada.",
        "ja": "CSSパターンや「広告」「Sponsored」といった短いラベルをもとに、ページ上の広告ブロックを非表示にします。独立したネットワークリクエストでない場合にも有効です。",
        "ko": "CSS 패턴과 \"광고\"/\"Sponsored\" 같은 짧은 라벨을 기준으로 페이지의 광고 블록을 숨깁니다. 별도의 네트워크 요청이 아닌 경우에도 작동합니다.",
        "de": "Blendet Werbeblöcke auf der Seite anhand von CSS-Mustern und kurzen Kennzeichnungen wie „Anzeige“/„Sponsored“ aus, auch wenn es sich nicht um eine eigene Netzwerkanfrage handelt.",
        "fr": "Masque les blocs publicitaires de la page selon des motifs CSS et de courtes mentions comme « Publicité »/« Sponsorisé », même quand il ne s'agit pas d'une requête réseau distincte.",
        "id": "Menyembunyikan blok iklan di halaman berdasarkan pola CSS dan label singkat seperti \"Iklan\"/\"Sponsored\", bahkan jika itu bukan permintaan jaringan terpisah.",
    },
    "heuristic_iframe_title": {
        "ru": "Эвристика по размеру iframe", "en": "Iframe-size heuristic", "zh_CN": "iframe 尺寸启发式检测",
        "es": "Heurística por tamaño de iframe", "hi": "iframe साइज़ हेयुरिस्टिक", "ar": "استدلال حسب حجم الإطار (iframe)",
        "pt_BR": "Heurística por tamanho de iframe", "ja": "iframeサイズによるヒューリスティック", "ko": "iframe 크기 휴리스틱",
        "de": "Iframe-Größen-Heuristik", "fr": "Heuristique par taille d'iframe", "id": "Heuristik ukuran iframe",
    },
    "badge_experimental": {
        "ru": "эксперимент", "en": "experimental", "zh_CN": "实验性",
        "es": "experimental", "hi": "प्रायोगिक", "ar": "تجريبي",
        "pt_BR": "experimental", "ja": "実験的", "ko": "실험적",
        "de": "experimentell", "fr": "expérimental", "id": "eksperimental",
    },
    "heuristic_iframe_hint": {
        "ru": "Скрывает iframe стандартных рекламных размеров (300×250, 728×90 и т.д.) с чужого домена — ловит рекламу через собственный прокси-домен сайта, которую обычные списки не видят. Выключено по умолчанию: риск ложных срабатываний выше, чем у списков.",
        "en": "Hides iframes with standard ad sizes (300×250, 728×90, etc.) served from a different domain — catches ads a site serves through its own proxy domain, which regular lists can't see. Off by default: the risk of false positives is higher than with lists.",
        "zh_CN": "隐藏来自其他域名、尺寸符合标准广告规格(300×250、728×90 等)的 iframe——用于捕获网站通过自有代理域名投放、常规列表无法识别的广告。默认关闭:误判风险高于常规列表。",
        "es": "Oculta iframes con tamaños publicitarios estándar (300×250, 728×90, etc.) que provienen de un dominio distinto — detecta anuncios que el sitio sirve a través de su propio dominio proxy, algo que las listas normales no ven. Desactivado por defecto: el riesgo de falsos positivos es mayor que con las listas.",
        "hi": "अलग डोमेन से आने वाले, स्टैंडर्ड विज्ञापन साइज़ (300×250, 728×90 आदि) वाले iframe को छुपाता है — यह उन विज्ञापनों को पकड़ता है जिन्हें साइट अपने ही प्रॉक्सी डोमेन के ज़रिए दिखाती है, जिन्हें सामान्य सूचियाँ नहीं देख पातीं। डिफ़ॉल्ट रूप से बंद है: इसमें गलत पहचान का जोखिम सूचियों से ज़्यादा है।",
        "ar": "يُخفي إطارات iframe بأحجام إعلانية قياسية (300×250، 728×90 وغيرها) قادمة من نطاق مختلف — يلتقط الإعلانات التي يعرضها الموقع عبر نطاق وكيل خاص به، وهو ما لا تراه القوائم العادية. مُعطَّل افتراضيًا: خطر الإيجابيات الكاذبة أعلى منه في القوائم.",
        "pt_BR": "Oculta iframes com tamanhos publicitários padrão (300×250, 728×90 etc.) vindos de um domínio diferente — detecta anúncios que o site serve pelo próprio domínio proxy, algo que as listas comuns não enxergam. Desativado por padrão: o risco de falsos positivos é maior do que com as listas.",
        "ja": "別ドメインから配信される、標準的な広告サイズ(300×250、728×90など)のiframeを非表示にします。サイトが自社のプロキシドメイン経由で配信する、通常のリストでは検出できない広告を捕捉します。誤検知のリスクがリストより高いため、デフォルトではオフです。",
        "ko": "다른 도메인에서 제공되는 표준 광고 크기(300×250, 728×90 등)의 iframe을 숨깁니다 — 사이트가 자체 프록시 도메인을 통해 제공하는, 일반 목록으로는 감지되지 않는 광고를 잡아냅니다. 오탐 위험이 목록 방식보다 높아 기본적으로 꺼져 있습니다.",
        "de": "Blendet Iframes mit Standard-Werbegrößen (300×250, 728×90 usw.) aus, die von einer anderen Domain stammen — erkennt Werbung, die eine Website über ihre eigene Proxy-Domain ausliefert und die normale Listen nicht sehen. Standardmäßig deaktiviert: Das Risiko von Fehlalarmen ist höher als bei Listen.",
        "fr": "Masque les iframes aux tailles publicitaires standards (300×250, 728×90, etc.) provenant d'un autre domaine — détecte les publicités qu'un site diffuse via son propre domaine proxy, invisibles pour les listes classiques. Désactivé par défaut : le risque de faux positifs est plus élevé qu'avec les listes.",
        "id": "Menyembunyikan iframe berukuran iklan standar (300×250, 728×90, dll.) yang berasal dari domain berbeda — menangkap iklan yang disajikan situs melalui domain proksinya sendiri, yang tidak terlihat oleh daftar biasa. Nonaktif secara default: risiko positif palsu lebih tinggi dibanding daftar.",
    },
    "section_stats": {
        "ru": "Статистика", "en": "Statistics", "zh_CN": "统计",
        "es": "Estadísticas", "hi": "आँकड़े", "ar": "الإحصائيات",
        "pt_BR": "Estatísticas", "ja": "統計", "ko": "통계",
        "de": "Statistik", "fr": "Statistiques", "id": "Statistik",
    },
    "stat_total_blocked": {
        "ru": "заблокировано всего", "en": "blocked in total", "zh_CN": "累计拦截数",
        "es": "bloqueados en total", "hi": "कुल ब्लॉक", "ar": "إجمالي المحظور",
        "pt_BR": "bloqueado no total", "ja": "累計ブロック数", "ko": "총 차단 수",
        "de": "insgesamt blockiert", "fr": "bloqués au total", "id": "total diblokir",
    },
    "stat_since": {
        "ru": "расширение работает с", "en": "extension running since", "zh_CN": "扩展程序启用于",
        "es": "la extensión funciona desde", "hi": "एक्सटेंशन चल रहा है", "ar": "الإضافة تعمل منذ",
        "pt_BR": "extensão em funcionamento desde", "ja": "拡張機能の稼働開始日", "ko": "확장 프로그램 사용 시작일",
        "de": "Erweiterung aktiv seit", "fr": "extension active depuis", "id": "ekstensi berjalan sejak",
    },
    "section_whitelist": {
        "ru": "Разрешённые сайты", "en": "Allowed sites", "zh_CN": "已允许的网站",
        "es": "Sitios permitidos", "hi": "अनुमति प्राप्त साइटें", "ar": "المواقع المسموح بها",
        "pt_BR": "Sites permitidos", "ja": "許可済みサイト", "ko": "허용된 사이트",
        "de": "Erlaubte Websites", "fr": "Sites autorisés", "id": "Situs yang diizinkan",
    },
    "whitelist_hint": {
        "ru": "На этих сайтах вы разрешили показ рекламы — переключатель можно найти в попапе расширения.",
        "en": "You've allowed ads to show on these sites — you'll find the toggle in the extension's popup.",
        "zh_CN": "您已在这些网站上允许显示广告——该开关可在扩展程序的弹出窗口中找到。",
        "es": "Has permitido que se muestren anuncios en estos sitios — encontrarás el interruptor en la ventana emergente de la extensión.",
        "hi": "आपने इन साइटों पर विज्ञापन दिखाने की अनुमति दी है — यह स्विच एक्सटेंशन के पॉपअप में मिलेगा।",
        "ar": "لقد سمحت بعرض الإعلانات في هذه المواقع — يمكنك العثور على المفتاح في نافذة الإضافة المنبثقة.",
        "pt_BR": "Você permitiu a exibição de anúncios nestes sites — o interruptor fica no popup da extensão.",
        "ja": "これらのサイトでは広告の表示を許可しています。切り替えスイッチは拡張機能のポップアップにあります。",
        "ko": "이 사이트들에서는 광고 표시를 허용하셨습니다 — 토글은 확장 프로그램 팝업에서 찾을 수 있습니다.",
        "de": "Auf diesen Websites hast du Werbung erlaubt — den Schalter dafür findest du im Popup der Erweiterung.",
        "fr": "Vous avez autorisé l'affichage des publicités sur ces sites — le bouton se trouve dans la fenêtre contextuelle de l'extension.",
        "id": "Anda telah mengizinkan iklan tampil di situs-situs ini — sakelarnya ada di popup ekstensi.",
    },
    "whitelist_empty": {
        "ru": "Список пуст.", "en": "The list is empty.", "zh_CN": "列表为空。",
        "es": "La lista está vacía.", "hi": "सूची खाली है।", "ar": "القائمة فارغة.",
        "pt_BR": "A lista está vazia.", "ja": "リストは空です。", "ko": "목록이 비어 있습니다.",
        "de": "Die Liste ist leer.", "fr": "La liste est vide.", "id": "Daftar kosong.",
    },
    "remove_button": {
        "ru": "Убрать", "en": "Remove", "zh_CN": "移除",
        "es": "Quitar", "hi": "हटाएं", "ar": "إزالة",
        "pt_BR": "Remover", "ja": "削除", "ko": "제거",
        "de": "Entfernen", "fr": "Retirer", "id": "Hapus",
    },
    "section_custom_rules": {
        "ru": "Свои правила", "en": "Custom rules", "zh_CN": "自定义规则",
        "es": "Reglas personalizadas", "hi": "कस्टम नियम", "ar": "قواعد مخصّصة",
        "pt_BR": "Regras personalizadas", "ja": "カスタムルール", "ko": "사용자 지정 규칙",
        "de": "Eigene Regeln", "fr": "Règles personnalisées", "id": "Aturan khusus",
    },
    "custom_rules_hint": {
        "ru": "Одно правило на строку. Просто домен — заблокировать, <code>@@домен</code> — явно разрешить (если что-то заблокировалось лишнее). Строки с <code>!</code> — комментарии.",
        "en": "One rule per line. A plain domain — blocks it, <code>@@domain</code> — explicitly allows it (if something got blocked by mistake). Lines starting with <code>!</code> are comments.",
        "zh_CN": "每行一条规则。直接填域名表示拦截,<code>@@域名</code> 表示明确放行(用于纠正误拦截)。以 <code>!</code> 开头的行为注释。",
        "es": "Una regla por línea. Un dominio simple — lo bloquea, <code>@@dominio</code> — lo permite explícitamente (si algo se bloqueó por error). Las líneas con <code>!</code> son comentarios.",
        "hi": "प्रत्येक लाइन में एक नियम। सिर्फ़ डोमेन लिखने से वह ब्लॉक होगा, <code>@@डोमेन</code> लिखने से वह साफ़ तौर पर अनुमति पाएगा (अगर कुछ गलती से ब्लॉक हो गया हो)। <code>!</code> से शुरू होने वाली लाइनें टिप्पणी मानी जाती हैं।",
        "ar": "قاعدة واحدة في كل سطر. كتابة النطاق فقط — يحظره، وكتابة <code>@@النطاق</code> — تسمح به صراحةً (إن حُظر شيء عن طريق الخطأ). الأسطر التي تبدأ بـ <code>!</code> تُعدّ تعليقات.",
        "pt_BR": "Uma regra por linha. Um domínio simples — bloqueia, <code>@@dominio</code> — permite explicitamente (caso algo tenha sido bloqueado por engano). Linhas com <code>!</code> são comentários.",
        "ja": "1行につき1つのルールです。ドメインだけを書くとブロック、<code>@@ドメイン</code>と書くと明示的に許可します(誤ってブロックされた場合など)。<code>!</code>で始まる行はコメントとして扱われます。",
        "ko": "한 줄에 규칙 하나씩 입력합니다. 도메인만 입력하면 차단, <code>@@도메인</code>은 명시적으로 허용합니다(잘못 차단된 항목이 있을 때 사용). <code>!</code>로 시작하는 줄은 주석으로 처리됩니다。".replace("。", "."),
        "de": "Eine Regel pro Zeile. Eine reine Domain — blockiert sie, <code>@@domain</code> — erlaubt sie ausdrücklich (falls versehentlich etwas blockiert wurde). Zeilen mit <code>!</code> sind Kommentare.",
        "fr": "Une règle par ligne. Un domaine seul — le bloque, <code>@@domaine</code> — l'autorise explicitement (si quelque chose a été bloqué par erreur). Les lignes commençant par <code>!</code> sont des commentaires.",
        "id": "Satu aturan per baris. Domain biasa — akan diblokir, <code>@@domain</code> — diizinkan secara eksplisit (jika ada yang terblokir secara keliru). Baris yang diawali <code>!</code> dianggap komentar.",
    },
    "save_rules_button": {
        "ru": "Сохранить правила", "en": "Save rules", "zh_CN": "保存规则",
        "es": "Guardar reglas", "hi": "नियम सहेजें", "ar": "حفظ القواعد",
        "pt_BR": "Salvar regras", "ja": "ルールを保存", "ko": "규칙 저장",
        "de": "Regeln speichern", "fr": "Enregistrer les règles", "id": "Simpan aturan",
    },
    "rules_saved": {
        "ru": "Сохранено ({count})", "en": "Saved ({count})", "zh_CN": "已保存({count})",
        "es": "Guardado ({count})", "hi": "सहेजा गया ({count})", "ar": "تم الحفظ ({count})",
        "pt_BR": "Salvo ({count})", "ja": "保存しました({count})", "ko": "저장됨({count})",
        "de": "Gespeichert ({count})", "fr": "Enregistré ({count})", "id": "Tersimpan ({count})",
    },
    "section_about": {
        "ru": "О расширении", "en": "About", "zh_CN": "关于",
        "es": "Acerca de", "hi": "इसके बारे में", "ar": "حول الإضافة",
        "pt_BR": "Sobre", "ja": "この拡張機能について", "ko": "정보",
        "de": "Über die Erweiterung", "fr": "À propos", "id": "Tentang",
    },
    "about_text_1": {
        "ru": "FlameBlock — полностью автономное расширение. Все правила и настройки хранятся локально в вашем браузере, никакие данные никуда не отправляются и не собираются. В архиве рядом лежат SPEC.md (что и как устроено) и RESEARCH.md (разбор техник блокировки и что из этого реально применимо на Chrome/Opera) — для тех, кому интересны детали.",
        "en": "FlameBlock is a fully self-contained extension. All rules and settings are stored locally in your browser — nothing is ever sent anywhere or collected. The archive also includes SPEC.md (how everything is built) and RESEARCH.md (a breakdown of blocking techniques and what's actually feasible on Chrome/Opera) for anyone curious about the details.",
        "zh_CN": "FlameBlock 是一个完全独立运行的扩展程序。所有规则和设置都保存在您本地的浏览器中,不会向任何地方发送或收集任何数据。压缩包中还附带了 SPEC.md(说明各部分的构建方式)和 RESEARCH.md(拦截技术的分析,以及哪些在 Chrome/Opera 上真正可行),供对细节感兴趣的用户查阅。",
        "es": "FlameBlock es una extensión completamente autónoma. Todas las reglas y ajustes se guardan localmente en tu navegador; no se envía ni se recopila ningún dato. En el archivo también encontrarás SPEC.md (cómo está construido todo) y RESEARCH.md (un análisis de las técnicas de bloqueo y qué es realmente viable en Chrome/Opera), por si te interesan los detalles.",
        "hi": "FlameBlock पूरी तरह से स्वतंत्र (autonomous) एक्सटेंशन है। सभी नियम और सेटिंग्स आपके ब्राउज़र में लोकल रूप से सेव रहती हैं, कोई भी डेटा कहीं भेजा या इकट्ठा नहीं किया जाता। आर्काइव में SPEC.md (सब कुछ कैसे बना है) और RESEARCH.md (ब्लॉकिंग तकनीकों का विश्लेषण और Chrome/Opera पर वास्तव में क्या लागू होता है) भी मौजूद हैं — उन लोगों के लिए जिन्हें विवरण में दिलचस्पी हो।",
        "ar": "FlameBlock إضافة مستقلة بالكامل. تُحفظ جميع القواعد والإعدادات محليًا في متصفحك، ولا تُرسل أو تُجمع أي بيانات إلى أي جهة. يحتوي الأرشيف أيضًا على SPEC.md (شرح لكيفية بناء كل شيء) وRESEARCH.md (تحليل لتقنيات الحظر وما هو قابل للتطبيق فعليًا على Chrome/Opera) لمن يهتم بالتفاصيل.",
        "pt_BR": "O FlameBlock é uma extensão totalmente autônoma. Todas as regras e configurações ficam armazenadas localmente no seu navegador, nenhum dado é enviado ou coletado. No arquivo também estão o SPEC.md (como tudo foi construído) e o RESEARCH.md (uma análise das técnicas de bloqueio e o que é realmente viável no Chrome/Opera), para quem tiver interesse nos detalhes.",
        "ja": "FlameBlockは完全に自己完結した拡張機能です。すべてのルールと設定はブラウザ内にローカル保存され、データがどこかへ送信されたり収集されたりすることはありません。アーカイブにはSPEC.md(仕組みの説明)とRESEARCH.md(ブロック技術の分析とChrome/Operaで実際に使える手法の検証)も含まれており、詳細に興味のある方はご覧いただけます。",
        "ko": "FlameBlock은 완전히 독립적으로 동작하는 확장 프로그램입니다. 모든 규칙과 설정은 브라우저에 로컬로 저장되며, 어떤 데이터도 어디로도 전송되거나 수집되지 않습니다. 아카이브에는 SPEC.md(전체 구조 설명)와 RESEARCH.md(차단 기술 분석 및 Chrome/Opera에서 실제로 적용 가능한 부분 정리)도 함께 들어 있어, 자세한 내용이 궁금하신 분들이 참고하실 수 있습니다.",
        "de": "FlameBlock ist eine vollständig eigenständige Erweiterung. Alle Regeln und Einstellungen werden lokal in deinem Browser gespeichert, es werden niemals Daten irgendwohin gesendet oder gesammelt. Im Archiv liegen außerdem SPEC.md (wie alles aufgebaut ist) und RESEARCH.md (eine Analyse der Blockiertechniken und was auf Chrome/Opera tatsächlich umsetzbar ist) für alle, die sich für die Details interessieren.",
        "fr": "FlameBlock est une extension entièrement autonome. Toutes les règles et tous les paramètres sont stockés localement dans votre navigateur, aucune donnée n'est jamais envoyée ni collectée. L'archive contient aussi SPEC.md (comment tout est construit) et RESEARCH.md (une analyse des techniques de blocage et de ce qui est réellement applicable sur Chrome/Opera), pour les curieux.",
        "id": "FlameBlock adalah ekstensi yang sepenuhnya mandiri. Semua aturan dan pengaturan disimpan secara lokal di browser Anda, tidak ada data yang pernah dikirim atau dikumpulkan. Arsipnya juga menyertakan SPEC.md (cara semuanya dibangun) dan RESEARCH.md (analisis teknik pemblokiran dan apa yang benar-benar dapat diterapkan di Chrome/Opera) bagi yang tertarik dengan detailnya.",
    },
    "about_text_2": {
        "ru": "Расширение абсолютно бесплатно для всех и всегда будет таким. Если оно вам пригодилось и есть желание поддержать разработку — будем очень благодарны, но это исключительно на ваше усмотрение.",
        "en": "The extension is completely free for everyone and always will be. If it's been useful to you and you'd like to support development, we'd be very grateful — but that's entirely up to you.",
        "zh_CN": "本扩展程序对所有人完全免费,并将永远保持免费。如果它对您有所帮助,并且您愿意支持开发,我们将非常感激——但这完全取决于您自己的意愿。",
        "es": "La extensión es totalmente gratuita para todos y siempre lo será. Si te ha resultado útil y quieres apoyar su desarrollo, te lo agradeceríamos mucho — pero es completamente opcional.",
        "hi": "यह एक्सटेंशन सभी के लिए पूरी तरह मुफ़्त है और हमेशा मुफ़्त ही रहेगा। अगर यह आपके काम आया है और आप डेवलपमेंट को सपोर्ट करना चाहें, तो हमें बहुत खुशी होगी — लेकिन यह पूरी तरह आपकी मर्ज़ी पर है।",
        "ar": "الإضافة مجانية بالكامل للجميع، وستظل كذلك دائمًا. إذا كانت مفيدة لك ورغبت في دعم تطويرها، سنكون ممتنين جدًا — لكن هذا الأمر يعود إليك تمامًا.",
        "pt_BR": "A extensão é totalmente gratuita para todos e sempre será. Se ela foi útil para você e quiser apoiar o desenvolvimento, ficaremos muito gratos — mas isso é totalmente opcional.",
        "ja": "この拡張機能はすべての人にとって完全に無料であり、これからもずっと無料です。もしお役に立てたなら、開発を支援していただけるととても嬉しいですが、それはあくまで任意です。",
        "ko": "이 확장 프로그램은 모두에게 완전히 무료이며 앞으로도 그럴 것입니다. 도움이 되셨고 개발을 후원하고 싶으시다면 정말 감사하겠습니다 — 다만 이는 전적으로 선택 사항입니다.",
        "de": "Die Erweiterung ist für alle vollkommen kostenlos und wird es immer bleiben. Wenn sie dir nützlich war und du die Entwicklung unterstützen möchtest, würden wir uns sehr freuen — das liegt aber ganz bei dir.",
        "fr": "L'extension est entièrement gratuite pour tous et le restera toujours. Si elle vous a été utile et que vous souhaitez soutenir son développement, nous vous en serions très reconnaissants — mais cela reste entièrement à votre discrétion.",
        "id": "Ekstensi ini sepenuhnya gratis untuk semua orang dan akan selalu begitu. Jika bermanfaat bagi Anda dan Anda ingin mendukung pengembangannya, kami akan sangat berterima kasih — namun itu sepenuhnya terserah Anda.",
    },
    "dev_label": {
        "ru": "Разработчик", "en": "Developer", "zh_CN": "开发者",
        "es": "Desarrollador", "hi": "डेवलपर", "ar": "المطوّر",
        "pt_BR": "Desenvolvedor", "ja": "開発者", "ko": "개발자",
        "de": "Entwickler", "fr": "Développeur", "id": "Pengembang",
    },
    "email_label": {
        "ru": "Почта", "en": "Email", "zh_CN": "邮箱",
        "es": "Correo", "hi": "ईमेल", "ar": "البريد الإلكتروني",
        "pt_BR": "E-mail", "ja": "メール", "ko": "이메일",
        "de": "E-Mail", "fr": "E-mail", "id": "Email",
    },
    "bic_label": {
        "ru": "БИК", "en": "BIC", "zh_CN": "BIC",
        "es": "BIC", "hi": "BIC", "ar": "BIC",
        "pt_BR": "BIC", "ja": "BIC", "ko": "BIC",
        "de": "BIC", "fr": "BIC", "id": "BIC",
    },
}

# --- строгая проверка полноты перед генерацией -----------------------------
missing = []
for key, by_locale in TRANSLATIONS.items():
    for loc in LOCALES:
        if loc not in by_locale or not by_locale[loc].strip():
            missing.append(f"{key} -> {loc}")
if missing:
    raise SystemExit("ОТСУТСТВУЮТ ПЕРЕВОДЫ (генерация остановлена):\n" + "\n".join(missing))

# --- генерация файлов --------------------------------------------------------
for loc in LOCALES:
    out_dir = os.path.join(BASE, "_locales", loc)
    os.makedirs(out_dir, exist_ok=True)
    payload = {key: {"message": by_locale[loc]} for key, by_locale in TRANSLATIONS.items()}
    with open(os.path.join(out_dir, "messages.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"Готово: {len(LOCALES)} языков x {len(TRANSLATIONS)} ключей = "
      f"{len(LOCALES) * len(TRANSLATIONS)} переведённых строк.")
