#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Патч №5 — по результатам adblock-tester.com (74/100, слабое место: Banner
Advertising — файлы-приманки типа pr_advertising_ads_banner.gif/.swf/.png,
раздаются с самого тестового сайта, поймать можно только по имени файла, не
по домену) и OBFUSGATED-теста (94%, 337/356 доменов — даёт точный список из
19 доменов, которые прошли мимо).

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
# 1. adblock-tester.com: "Banner advertising" — тест раздаёт свои же файлы
#    /banners/pr_advertising_ads_banner.{gif,png,swf} с САМОГО тестового сайта
#    (первого лица) — поймать можно только по говорящему имени файла.
#    .swf вообще безопасно резать целиком: Flash мёртв с 2020 года, ни один
#    легитимный сайт больше не отдаёт .swf.
# ---------------------------------------------------------------------------

GENERIC_BANNER_PATTERNS = [
    "advertising_ads_banner", "ads_banner.", "_ads_banner", "advertising_ads",
]

# ---------------------------------------------------------------------------
# 2. OBFUSGATED-тест: точный список из 19 не заблокированных доменов.
#    Из них НАМЕРЕННО пропускаем 6 — это те же общие домены с законным
#    неадовым использованием, что я уже исключал раньше (ядро видео YouTube и
#    общий Facebook/Instagram Graph API) — блокировка сломала бы чужую
#    функциональность, а не только рекламу.
# ---------------------------------------------------------------------------

SKIP_SHARED_API = {
    "s.youtube.com", "redirector.googlevideo.com", "youtubei.googleapis.com",
    "graph.facebook.com", "graph.instagram.com", "i.instagram.com",
}

OBFUSGATED_NOT_BLOCKED = [
    "s.youtube.com", "redirector.googlevideo.com", "youtubei.googleapis.com",
    "tagmanager.google.com", "quantcast.com", "thetradedesk.com", "api.rlcdn.com",
    "kochava.com", "crypto-loot.org", "greatis.com", "graph.facebook.com",
    "graph.instagram.com", "i.instagram.com", "d.reddit.com",
    "settings-win.data.microsoft.com", "vortex-win.data.microsoft.com",
    "watson.telemetry.microsoft.com", "cd.connatix.com", "vid.connatix.com",
]

# connatix.com у нас был представлен только отдельными поддоменами
# (capi./ck./ins./lit./pl.connatix.com), а не самим доменом — поэтому
# cd./vid.connatix.com проходили мимо. Правильный фикс — базовый домен,
# он по правилам DNR покрывает вообще все поддомены разом.
ADS_NEW = [d for d in OBFUSGATED_NOT_BLOCKED if d not in SKIP_SHARED_API
           and d not in ("cd.connatix.com", "vid.connatix.com")] + ["connatix.com"]

ADS_TYPES = ["main_frame", "sub_frame", "script", "image", "xmlhttprequest",
             "media", "font", "object", "ping", "other", "websocket", "stylesheet"]
BANNER_TYPES = ["image", "media", "object", "other"]

ads_path = os.path.join(BASE, "rules", "ads.json")

banner_total, banner_added = append_generic_rules(ads_path, GENERIC_BANNER_PATTERNS, BANNER_TYPES)
swf_total, swf_added = append_generic_rules(ads_path, [".swf"], ["object", "media", "other"])
ads_total, ads_added = append_domain_rules(ads_path, ADS_NEW, ADS_TYPES)

trk_total = len(load_rules(os.path.join(BASE, "rules", "trackers.json")))
aab_total = len(load_rules(os.path.join(BASE, "rules", "antiadblock.json")))
grand_total = ads_total + trk_total + aab_total

print(f"generic banner-правила: +{banner_added}")
print(f"generic .swf правило:   +{swf_added}")
print(f"ads.json домены:        +{ads_added} (из {len(ADS_NEW)}) -> итого {ads_total}")
print(f"пропущено намеренно (общие API): {len(SKIP_SHARED_API)}")
print(f"ВСЕГО ПРАВИЛ: {grand_total} (лимит 30000)")
