#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Патч №3 — домены из полного состава двух дополнительных тестов (Super Adblock
Test, 507 проверок, среди них Consent/A-B/Social категории). Список собран из
самого HTML присланных .mhtml-отчётов: все домены, похожие на рекламные/
трекинговые, за вычетом небольшого списка ИСКЛЮЧЕНИЙ — общих API-доменов,
у которых есть законное не-рекламное использование (например graph.facebook.com
используется и для обычного "Войти через Facebook", блокировать его целиком
было бы избыточно и могло сломать чужие сайты).

Как и раньше — только ДОБАВЛЯЕТ, дубли по домену пропускаются автоматически.
"""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# домены, которые НЕ добавляем — общие API/CDN с законным не-рекламным
# использованием, блокировать целиком рискованно для чужой функциональности
SKIP = {
    "graph.facebook.com", "graph.instagram.com", "i.instagram.com",
    "www.facebook.com", "google-analytics.com", "googletagmanager.com",
    "www.google-analytics.com", "www.googletagmanager.com",
}

ADS_NEW = [
    "a.teads.tv", "cdn.teads.tv", "aax.amazon-adsystem.com", "c.amazon-adsystem.com",
    "ir-na.amazon-adsystem.com", "rcm-na.amazon-adsystem.com", "mads-eu.amazon.com",
    "mads.amazon-adsystem.com", "s.amazon-adsystem.com", "fls-na.amazon-adsystem.com",
    "device-metrics-us.amazon.com", "device-metrics-us-2.amazon.com",
    "ad.doubleclick.net", "adclick.g.doubleclick.net", "cm.g.doubleclick.net",
    "googleads.g.doubleclick.net", "googleads4.g.doubleclick.net", "m.doubleclick.net",
    "mediavisor.doubleclick.net", "pagead.l.doubleclick.net", "pubads.g.doubleclick.net",
    "securepubads.g.doubleclick.net", "stats.g.doubleclick.net",
    "bingads.microsoft.com", "cdn.ads.microsoft.com",
    "mcs-va.tiktokv.com", "mon.tiktokv.com",
    "insights.adsrvr.org", "match.adsrvr.org", "bid.adsrvr.org", "insight.adsrvr.org", "js.adsrvr.org",
    "onclickads.net", "popmyads.com", "onetag-sys.com",
    "ads.pubmatic.com", "gads.pubmatic.com", "optimized-by.rubiconproject.com",
    "ads.rubiconproject.com", "pixel.rubiconproject.com",
    "ads.sovrn.com", "ads.snapchat.com", "ads.roku.com", "p.ads.roku.com",
    "ads.vizio.com", "ads.stickyadstv.com", "ads.tremorhub.com",
    "ad.lgappstv.com", "info.lgsmartad.com", "us.info.lgsmartad.com",
    "display.ad.daum.net", "track.tiara.daum.net",
    "ad.zanox.com", "ad.linksynergy.com", "analytics.linksynergy.com",
    "track.webgains.com", "track.webgains.org",
    "ads.nexage.com", "ads.api.vungle.com", "config.ads.vungle.com", "events.ads.vungle.com",
    "track.adform.net", "gslbeacon.lijit.com", "adserver-us.adtech.advertising.com",
    "ads-api.nextdoor.com", "pixel.nextdoor.com", "amplifypixel.outbrain.com",
    "pixel.mathtag.com", "pixel.quantserve.com", "pixel.quora.com", "pixel.redditmedia.com",
    "fw.adsafeprotected.com", "pixel.adsafeprotected.com", "cmp.inmobi.com",
    "init.supersonicads.com", "outcome-ssp.supersonicads.com",
    "ads.huawei.com", "ads.x.com", "ads-api.x.com", "analytics.x.com",
    "config.samsungads.com", "globalapi.ad.xiaomi.com",
    "adserver.unityads.unity3d.com", "webview.unityads.unity3d.com",
]

TRACKERS_NEW = [
    "id5-sync.com", "idsync.rlcdn.com", "ad.crwdcntrl.net",
    "heapanalytics.com", "cdn.heapanalytics.com", "c.heapanalytics.com",
    "analytics.adobe.io", "metrics.brightcove.com", "metrics.apple.com",
    "tracking.crazyegg.com", "tracker.kochava.com", "api.optimizely.com",
    "consentcdn.cookiebot.com", "cookie-cdn.cookiepro.com", "imgsct.cookiebot.com",
    "cmp.quantcast.com", "cmp.usercentrics.eu",
]


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
        if d in SKIP or d in have:
            continue
        have.add(d)
        rules.append({
            "id": next_id, "priority": 1, "action": {"type": "block"},
            "condition": {"urlFilter": f"||{d}^", "resourceTypes": resource_types},
        })
        next_id += 1
        added += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, separators=(",", ":"))
    return len(rules), added


ADS_TYPES = ["main_frame", "sub_frame", "script", "image", "xmlhttprequest",
             "media", "font", "object", "ping", "other", "websocket", "stylesheet"]
TRACKERS_TYPES = ["sub_frame", "script", "image", "xmlhttprequest", "ping", "other", "media", "websocket"]

ads_total, ads_added = append_rules(os.path.join(BASE, "rules", "ads.json"), ADS_NEW, ADS_TYPES)
trk_total, trk_added = append_rules(os.path.join(BASE, "rules", "trackers.json"), TRACKERS_NEW, TRACKERS_TYPES)
aab_total = len(load_rules(os.path.join(BASE, "rules", "antiadblock.json")))

grand_total = ads_total + trk_total + aab_total
print(f"ads.json:        +{ads_added:>5} новых -> итого {ads_total}")
print(f"trackers.json:    +{trk_added:>5} новых -> итого {trk_total}")
print(f"пропущено как рискованные (общие API-домены): {len(SKIP)}")
print(f"ВСЕГО ПРАВИЛ:      {grand_total} (лимит Chrome GUARANTEED_MINIMUM_STATIC_RULES = 30000)")
