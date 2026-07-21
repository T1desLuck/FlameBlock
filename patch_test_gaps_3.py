#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Патч №4 — по результатам двух новых тестов:
  1. "Ad Scripts Loading" тест (turtlecute.org) проверяет, ловим ли мы скрипт по
     ИМЕНИ ФАЙЛА вообще без привязки к домену (первый источник — сам тестовый
     сайт, first-party). Раньше у нас были только правила вида ||домен^ — они
     физически не могут поймать такое. Нужны generic-правила БЕЗ домена-якоря.
  2. Второй тест показал точные слабые места после патчей 1-3: Email Tracking &
     Live Chat, Affiliate Networks, A/B Testing — плюс попутно вскрылись
     крипто-майнинг скрипты (coinimp, minero и т.п.), которые вообще не реклама,
     но однозначно стоит блокировать.

Как и раньше — только ДОБАВЛЯЕТ, ничего не удаляя и не трогая.
"""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def load_rules(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def existing_domains(rules):
    return {r.get("condition", {}).get("urlFilter", "").strip("|^") for r in rules}


def append_domain_rules(path, new_domains, resource_types):
    rules = load_rules(path)
    have = existing_domains(rules)
    next_id = max((r["id"] for r in rules), default=0) + 1
    added = 0
    for d in new_domains:
        if d in have:
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


def append_generic_rules(path, patterns, resource_types):
    """Правила БЕЗ || -якоря — совпадение по подстроке в любом месте URL,
    независимо от домена. Используем только для узкого, проверенного набора
    файловых имён скриптов, однозначно связанных с рекламой — не трогаем ничего
    похожего на обычные общеупотребимые имена файлов."""
    rules = load_rules(path)
    have = {r.get("condition", {}).get("urlFilter", "") for r in rules}
    next_id = max((r["id"] for r in rules), default=0) + 1
    added = 0
    for pat in patterns:
        if pat in have:
            continue
        have.add(pat)
        rules.append({
            "id": next_id, "priority": 1, "action": {"type": "block"},
            "condition": {"urlFilter": pat, "resourceTypes": resource_types},
        })
        next_id += 1
        added += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, separators=(",", ":"))
    return len(rules), added


# ---------------------------------------------------------------------------
# 1. Generic-правила по имени файла скрипта (БЕЗ привязки к домену) — узкий,
#    проверенный набор: только файлы, чьё название однозначно рекламное.
# ---------------------------------------------------------------------------

GENERIC_SCRIPT_PATTERNS = [
    "/pagead.js", "/pagead2.js", "/ads.js", "/adsbygoogle.js",
    "/ad-loader.js", "/adloader.js",
]

# ---------------------------------------------------------------------------
# 2. Домены из полного состава второго теста, которых у нас ещё не было —
#    отфильтрованы вручную: исключены общие CDN/API с законным неадовым
#    использованием (cdn.jsdelivr.net, graph.facebook.com, redirector.
#    googlevideo.com и т.п. — блокировка сломала бы чужую функциональность)
# ---------------------------------------------------------------------------

ADS_NEW = [
    "media.net", "adjust.com", "adlog.vivo.com", "ads-api.vivo.com",
    "advertising-api-eu.amazon.com", "advertising.apple.com", "advertising.yahoo.com",
    "amoeba.web.roku.com", "logs.roku.com", "api.fyber.com", "live.chartboost.com",
    "ironsource.mobi", "pangleglobal.com", "yumenetworks.com", "liftoff.io",
    "smartclip.com", "smartclip.net", "smartyads.com", "stackadapt.com",
    "insightexpressai.com", "htlbid.com", "apex.go.sonobi.com", "cdn.indexexchange.com",
    "indexexchange.com", "cdn.kargo.com", "sync.kargo.com", "stickyadstv.com",
    "imasdk.googleapis.com", "dai.google.com", "trafficjunky.net",
    "fundingchoicesmessages.google.com", "ngfts.lge.com", "us.ibs.lgappstv.com",
    "udc.yahoo.com", "mon.byteoversea.com", "offerwall.yandex.net",
    "g.jwpsrv.com", "prd.jwpltx.com", "ssl.p.jwpcdn.com", "c.bing.com",
    "xp.apple.com", "a.lenovo.com", "nmetrics.samsung.com",
    # криптомайнинг-скрипты — не реклама, но однозначно нежелательны
    "coinimp.com", "www.coinimp.com", "minero.cc", "monerominer.rocks", "webminepool.com",
]

TRACKERS_NEW = [
    # Email tracking & live chat
    "a.klaviyo.com", "klaviyo.com", "static.klaviyo.com", "click.mailchimp.com",
    "list-manage.com", "js.driftt.com", "widget.intercom.io",
    "api.onesignal.com", "cdn.onesignal.com",
    # Affiliate networks — самая слабая категория второго теста
    "go.skimresources.com", "redirect.viglink.com", "s.skimresources.com",
    "redirector.skimresources.com", "cdn.viglink.com", "api.viglink.com",
    "viglink.com", "skimresources.com", "impact.com", "api.impact.com",
    "prf.hn", "t.pepperjamnetwork.com", "partnerstack.com", "api.partnerstack.com",
    "bnc.lt", "app.appsflyer.com", "appsflyer.com", "app-measurement.com",
    "control.kochava.com",
    # A/B testing / персонализация — усиление
    "st.dynamicyield.com", "cdn.dynamicyield.com",
    # общая аналитика/трекинг
    "posthog.com", "app.posthog.com", "eu.posthog.com", "us.i.posthog.com",
    "rudderstack.com", "snowplowanalytics.com", "tracker.snowplowanalytics.com",
    "cloudflareinsights.com", "static.cloudflareinsights.com", "fingerprintjs.com",
    "snap.licdn.com", "tr.facebook.com", "analytics.twitter.com", "metrics.adobe.com",
    "px.srvcs.tumblr.com", "qevents.quora.com", "sc-analytics.appspot.com",
    "mineralt.io", "statdynamic.com",
]

ADS_TYPES = ["main_frame", "sub_frame", "script", "image", "xmlhttprequest",
             "media", "font", "object", "ping", "other", "websocket", "stylesheet"]
TRACKERS_TYPES = ["sub_frame", "script", "image", "xmlhttprequest", "ping", "other", "media", "websocket"]

ads_path = os.path.join(BASE, "rules", "ads.json")
trackers_path = os.path.join(BASE, "rules", "trackers.json")

script_total, script_added = append_generic_rules(ads_path, GENERIC_SCRIPT_PATTERNS, ["script"])
ads_total, ads_added = append_domain_rules(ads_path, ADS_NEW, ADS_TYPES)
trk_total, trk_added = append_domain_rules(trackers_path, TRACKERS_NEW, TRACKERS_TYPES)
aab_total = len(load_rules(os.path.join(BASE, "rules", "antiadblock.json")))

grand_total = ads_total + trk_total + aab_total
print(f"generic script-правила: +{script_added} (без привязки к домену)")
print(f"ads.json:      +{ads_added:>4} доменов -> итого {ads_total}")
print(f"trackers.json:  +{trk_added:>4} доменов -> итого {trk_total}")
print(f"ВСЕГО ПРАВИЛ:    {grand_total} (лимит 30000)")
