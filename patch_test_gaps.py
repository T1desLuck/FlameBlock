#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Патч №2 rules/*.json — на основе РЕАЛЬНЫХ результатов тестов (d3ward-style Ad
Blocker Test: 75/133 = 56%, категория Consent Management: 13%/0%, A/B Testing:
14%). ДОБАВЛЯЕТ поверх существующих файлов, ничего не удаляя и не меняя.

Источники добавляемых доменов:
  1. 55 доменов, ТОЧНО зафиксированных как "not blocked" в присланном отчёте
     теста — самый надёжный источник из всех, взято прямо из результата.
  2. Автоизвлечение простых правил ||domain^ из уже скачанных официальных
     файлов EasyList: easylist_cookie/*_thirdparty.txt и
     fanboy-addon/fanboy_*_thirdparty.txt — это и есть тот самый "Fanboy
     annoyances", который упоминался: consent/cookie-баннеры, notification-
     попапы, соцсети-виджеты. Ровно то, что просело до 13%/0% в тесте.
  3. Вручную проверенный список крупных CMP (Consent Management Platform) и
     A/B-тестинг сервисов, которых нет в EasyList в простом формате.
"""

import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "easylist-master")

SIMPLE_RE = re.compile(r"^\|\|([a-zA-Z0-9.\-]+)\^(?:\$([a-zA-Z\-,]+))?$")
ALLOWED_OPTIONS = {"third-party", "important", "popup", "first-party"}


def extract_domains(path, limit=None):
    domains = []
    if not os.path.exists(path):
        return domains
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            m = SIMPLE_RE.match(line)
            if not m:
                continue
            domain, opts = m.group(1), m.group(2)
            if opts and not set(opts.split(",")).issubset(ALLOWED_OPTIONS):
                continue
            if domain.startswith(".") or domain.endswith(".") or ".." in domain or "." not in domain:
                continue
            domains.append(domain.lower())
            if limit and len(domains) >= limit:
                break
    return domains


def load_rules(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def existing_domains(rules):
    return {r.get("condition", {}).get("urlFilter", "").strip("|^") for r in rules}


def append_rules(path, new_domains, resource_types):
    rules = load_rules(path)
    have = existing_domains(rules)
    next_id = max((r["id"] for r in rules), default=0) + 1
    added = 0
    for d in new_domains:
        if d in have:
            continue
        have.add(d)
        rules.append({
            "id": next_id,
            "priority": 1,
            "action": {"type": "block"},
            "condition": {"urlFilter": f"||{d}^", "resourceTypes": resource_types},
        })
        next_id += 1
        added += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, separators=(",", ":"))
    return len(rules), added


# ---------------------------------------------------------------------------
# 1. Домены, ЗАФИКСИРОВАННЫЕ как "not blocked" в присланном отчёте теста
# ---------------------------------------------------------------------------

CONFIRMED_MISSING = [
    "adc3-launch.adcolony.com", "ads-api.tiktok.com", "ads-api.twitter.com",
    "ads-sg.tiktok.com", "ads.linkedin.com", "ads.pinterest.com", "ads.tiktok.com",
    "ads.yahoo.com", "ads.youtube.com", "ads30.adcolony.com", "adsfs.oppomobile.com",
    "adtech.yahooinc.com", "adx.ads.oppomobile.com", "an.facebook.com",
    "analytics.query.yahoo.com", "analytics.s3.amazonaws.com",
    "analyticsengine.s3.amazonaws.com", "api-adservices.apple.com",
    "api.ad.xiaomi.com", "app.getsentry.com", "bdapi-ads.realmemobile.com",
    "bdapi-in-ads.realmemobile.com", "books-analytics-events.apple.com",
    "browser.sentry-cdn.com", "business-api.tiktok.com", "ck.ads.oppomobile.com",
    "click.googleanalytics.com", "data.ads.oppomobile.com",
    "data.mistat.india.xiaomi.com", "data.mistat.rus.xiaomi.com",
    "data.mistat.xiaomi.com", "events.reddit.com", "events.redditmedia.com",
    "events3alt.adcolony.com", "gemini.yahoo.com", "geo.yahoo.com",
    "grs.hicloud.com", "iadsdk.apple.com", "iot-eu-logser.realme.com",
    "iot-logser.realme.com", "log.byteoversea.com", "log.fc.yahoo.com",
    "metrika.yandex.ru", "notes-analytics-events.apple.com",
    "partnerads.ysm.yahoo.com", "pixel.facebook.com", "samsungads.com",
    "sdkconfig.ad.intl.xiaomi.com", "sdkconfig.ad.xiaomi.com",
    "smetrics.samsung.com", "static.ads-twitter.com", "tracking.rus.miui.com",
    "udcm.yahoo.com", "wd.adcolony.com", "weather-analytics-events.apple.com",
]

# ---------------------------------------------------------------------------
# 2. Вручную проверенные CMP (баннеры согласия) и A/B-тестинг платформы —
#    именно та категория, что просела до 13%/0% в отчёте
# ---------------------------------------------------------------------------

CMP_AND_AB_TESTING = [
    # Consent Management Platforms
    "cdn.cookielaw.org", "cookielaw.org", "geolocation.onetrust.com", "onetrust.com",
    "consent.cookiebot.com", "cookiebot.com", "consent.cookiepro.com",
    "quantcast.mgr.consensu.org", "consent.quantcast.com",
    "consent.trustarc.com", "trustarc.com",
    "sdk.privacy-center.org", "consent.didomi.io", "didomi.io",
    "app.usercentrics.eu", "usercentrics.eu",
    "cmp.osano.com", "osano.com",
    "app.termly.io", "termly.io",
    "cdn.iubenda.com", "iubenda.com",
    "cdn-cookieyes.com", "cookieyes.com",
    "consensu.org", "privacy-mgmt.com", "sourcepoint.mgr.consensu.org",
    # A/B testing / experimentation
    "cdn.optimizely.com", "logx.optimizely.com", "optimizely.com",
    "dev.visualwebsiteoptimizer.com", "visualwebsiteoptimizer.com",
    "optimize.google.com", "abtasty.com", "kameleoon.com",
    "cdn-3.convertexperiments.com", "convertexperiments.com",
]

TRACKERS_TYPES = ["sub_frame", "script", "image", "xmlhttprequest", "ping", "other", "media", "websocket"]
ADS_TYPES = ["main_frame", "sub_frame", "script", "image", "xmlhttprequest",
             "media", "font", "object", "ping", "other", "websocket", "stylesheet"]

# ---------------------------------------------------------------------------
# 3. Автоизвлечение "Fanboy annoyances" + cookie thirdparty из EasyList —
#    источник, о котором сказал пользователь: cookie/notification/social
# ---------------------------------------------------------------------------

annoyance_domains = []
for fname in [
    "easylist_cookie/easylist_cookie_thirdparty.txt",
    "fanboy-addon/fanboy_annoyance_thirdparty.txt",
    "fanboy-addon/fanboy_notifications_thirdparty.txt",
    "fanboy-addon/fanboy_social_thirdparty.txt",
]:
    annoyance_domains += extract_domains(os.path.join(SRC, fname))

ads_path = os.path.join(BASE, "rules", "ads.json")
trackers_path = os.path.join(BASE, "rules", "trackers.json")

ads_total, ads_added = append_rules(ads_path, CONFIRMED_MISSING, ADS_TYPES)
trackers_total, trackers_added = append_rules(
    trackers_path, CMP_AND_AB_TESTING + annoyance_domains, TRACKERS_TYPES)

antiadblock_total = len(load_rules(os.path.join(BASE, "rules", "antiadblock.json")))
grand_total = ads_total + trackers_total + antiadblock_total

print(f"ads.json:        +{ads_added:>5} новых (из {len(CONFIRMED_MISSING)} по факту теста) -> итого {ads_total}")
print(f"trackers.json:    +{trackers_added:>5} новых (CMP/A-B: {len(CMP_AND_AB_TESTING)}, Fanboy/cookie: {len(annoyance_domains)}) -> итого {trackers_total}")
print(f"ВСЕГО ПРАВИЛ:      {grand_total} (лимит Chrome GUARANTEED_MINIMUM_STATIC_RULES = 30000)")
