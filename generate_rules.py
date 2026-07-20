#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор правил declarativeNetRequest (Manifest V3) для FlameBlock.

Безопасно извлекает ТОЛЬКО простые доменные правила вида ||domain^ (и ||domain^$third-party
/important/popup) из официальных списков EasyList / EasyPrivacy. Любые сложные строки
(косметические правила ##, regex /.../, правила с путями, wildcard *, domain=... и т.п.)
намеренно пропускаются — так исключается риск некорректного правила, которое могло бы
сломать загрузку всего набора правил в браузере.

Итоговый бюджет держим заметно ниже GUARANTEED_MINIMUM_STATIC_RULES = 30000
(гарантированный лимит Chrome на расширение), чтобы правила гарантированно
работали у пользователя вне зависимости от того, что ещё установлено в браузере.
"""

import json
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "easylist-master")
OUT = os.path.join(BASE, "rules")

SIMPLE_RE = re.compile(r"^\|\|([a-zA-Z0-9.\-]+)\^(?:\$([a-zA-Z\-,]+))?$")
ALLOWED_OPTIONS = {"third-party", "important", "popup", "first-party"}


def extract_domains(path, limit=None):
    """Достаём чистые домены из файла в формате EasyList, отбрасывая всё сложное."""
    domains = []
    if not os.path.exists(path):
        return domains
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("!"):
                continue
            m = SIMPLE_RE.match(line)
            if not m:
                continue
            domain, opts = m.group(1), m.group(2)
            if opts:
                tokens = set(opts.split(","))
                if not tokens.issubset(ALLOWED_OPTIONS):
                    continue
            if domain.startswith(".") or domain.endswith(".") or ".." in domain:
                continue
            if "." not in domain:
                continue
            domains.append(domain.lower())
            if limit and len(domains) >= limit:
                break
    return domains


def build_ruleset(domains, resource_types, id_start=1):
    rules = []
    rid = id_start
    seen = set()
    for d in domains:
        if d in seen:
            continue
        seen.add(d)
        rules.append({
            "id": rid,
            "priority": 1,
            "action": {"type": "block"},
            "condition": {
                "urlFilter": f"||{d}^",
                "resourceTypes": resource_types,
            },
        })
        rid += 1
    return rules


# ---------------------------------------------------------------------------
# 1. Наш собственный проверенный список крупнейших и самых известных
#    рекламных / трекинговых сетей — включаем ПОЛНОСТЬЮ и без ограничений,
#    чтобы главные игроки блокировались гарантированно, даже если урезаем
#    выгрузку из EasyList.
# ---------------------------------------------------------------------------

CURATED_ADS = [
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "adservice.google.com", "pagead2.googlesyndication.com", "2mdn.net",
    "googletagservices.com", "amazon-adsystem.com", "ads.microsoft.com",
    "adnxs.com", "casalemedia.com", "pubmatic.com", "rubiconproject.com",
    "openx.net", "criteo.com", "criteo.net", "taboola.com", "outbrain.com",
    "mgid.com", "smartadserver.com", "adform.net", "adroll.com", "media.net",
    "sovrn.com", "indexww.com", "triplelift.com", "teads.tv", "yieldmo.com",
    "sharethrough.com", "spotxchange.com", "spotx.tv", "tremorhub.com",
    "exoclick.com", "propellerads.com", "popads.net", "adcash.com",
    "revcontent.com", "zergnet.com", "plista.com", "bidswitch.net",
    "adsrvr.org", "smaato.com", "gumgum.com", "adyoulike.com", "content.ad",
    "bidvertiser.com", "infolinks.com", "juicyads.com", "trafficjunky.com",
    "clickadu.com", "hilltopads.net", "adsterra.com", "popcash.net",
    "adskeeper.co.uk", "an.yandex.ru", "adfox.yandex.ru", "ads.adfox.ru",
    "yabs.yandex.ru", "top-fwz1.mail.ru", "adriver.ru", "directadvert.ru",
    "ad.mail.ru",
]

CURATED_TRACKERS = [
    "google-analytics.com", "googletagmanager.com", "mc.yandex.ru",
    "hotjar.com", "mixpanel.com", "segment.io", "amplitude.com",
    "scorecardresearch.com", "quantserve.com", "chartbeat.com",
    "doubleverify.com", "moatads.com", "adsafeprotected.com",
    "fullstory.com", "crazyegg.com", "mouseflow.com", "connect.facebook.net",
    "analytics.tiktok.com", "px.ads.linkedin.com", "bat.bing.com",
]

CURATED_ANTIADBLOCK = [
    "blockadblock.com", "getadmiral.com", "pagefair.net", "pagefair.com",
    "blockthrough.com", "sourcepoint.com", "sp-prod.net",
]

# ---------------------------------------------------------------------------
# 2. Реальные community-списки EasyList / EasyPrivacy, скачанные из
#    официального репозитория github.com/easylist/easylist.
#    Урезаем количество, чтобы уложиться в безопасный бюджет.
# ---------------------------------------------------------------------------

ADS_BUDGET = 15000
TRACKERS_BUDGET = 7000
# admiral-список берём целиком без обрезки (он и так компактный)

el_adservers = extract_domains(os.path.join(SRC, "easylist/easylist_adservers.txt"), limit=ADS_BUDGET)
el_adservers_popup = extract_domains(os.path.join(SRC, "easylist/easylist_adservers_popup.txt"))

ep_general = extract_domains(os.path.join(SRC, "easyprivacy/easyprivacy_general.txt"))
ep_thirdparty = extract_domains(os.path.join(SRC, "easyprivacy/easyprivacy_thirdparty.txt"))
ep_trackingservers = extract_domains(os.path.join(SRC, "easyprivacy/easyprivacy_trackingservers.txt"))
ep_trackingservers_general = extract_domains(os.path.join(SRC, "easyprivacy/easyprivacy_trackingservers_general.txt"))
ep_trackingservers_thirdparty = extract_domains(os.path.join(SRC, "easyprivacy/easyprivacy_trackingservers_thirdparty.txt"))
ep_admiral = extract_domains(os.path.join(SRC, "easyprivacy/easyprivacy_trackingservers_admiral.txt"))
ep_notifications = extract_domains(os.path.join(SRC, "easyprivacy/easyprivacy_trackingservers_notifications.txt"))

trackers_extracted = (ep_general + ep_thirdparty + ep_trackingservers +
                       ep_trackingservers_general + ep_trackingservers_thirdparty)
trackers_extracted = trackers_extracted[:TRACKERS_BUDGET]

# ---------------------------------------------------------------------------
# 3. Собираем финальные наборы (курируемые + извлечённые, без дублей)
# ---------------------------------------------------------------------------

ADS_ALL = CURATED_ADS + el_adservers + el_adservers_popup
TRACKERS_ALL = CURATED_TRACKERS + trackers_extracted
ANTIADBLOCK_ALL = CURATED_ANTIADBLOCK + ep_admiral + ep_notifications

ADS_TYPES = ["main_frame", "sub_frame", "script", "image", "xmlhttprequest",
             "media", "font", "object", "ping", "other", "websocket", "stylesheet"]
TRACKERS_TYPES = ["sub_frame", "script", "image", "xmlhttprequest", "ping",
                   "other", "media", "websocket"]
ANTIADBLOCK_TYPES = ["main_frame", "sub_frame", "script", "xmlhttprequest", "other"]

ads_rules = build_ruleset(ADS_ALL, ADS_TYPES)
trackers_rules = build_ruleset(TRACKERS_ALL, TRACKERS_TYPES)
antiadblock_rules = build_ruleset(ANTIADBLOCK_ALL, ANTIADBLOCK_TYPES)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "ads.json"), "w", encoding="utf-8") as f:
    json.dump(ads_rules, f, ensure_ascii=False, separators=(",", ":"))
with open(os.path.join(OUT, "trackers.json"), "w", encoding="utf-8") as f:
    json.dump(trackers_rules, f, ensure_ascii=False, separators=(",", ":"))
with open(os.path.join(OUT, "antiadblock.json"), "w", encoding="utf-8") as f:
    json.dump(antiadblock_rules, f, ensure_ascii=False, separators=(",", ":"))

total = len(ads_rules) + len(trackers_rules) + len(antiadblock_rules)
print(f"ads.json:         {len(ads_rules):>6} правил  (курировано {len(CURATED_ADS)} + EasyList {len(el_adservers)+len(el_adservers_popup)})")
print(f"trackers.json:     {len(trackers_rules):>6} правил  (курировано {len(CURATED_TRACKERS)} + EasyPrivacy {len(trackers_extracted)})")
print(f"antiadblock.json:  {len(antiadblock_rules):>6} правил  (курировано {len(CURATED_ANTIADBLOCK)} + Admiral/notifications {len(ep_admiral)+len(ep_notifications)})")
print(f"ИТОГО:             {total:>6} правил  (лимит Chrome GUARANTEED_MINIMUM_STATIC_RULES = 30000)")
