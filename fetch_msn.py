#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

# Lista över orter
cities = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

OUTPUT_FOLDER = "data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def slugify(city):
    """Gör om åäö till aao, osv, för engelska URL:en."""
    return city.lower().replace("å", "a").replace("ä", "a").replace("ö", "o")

def fetch_and_parse(city):
    slug = slugify(city)
    url = f"https://www.msn.com/en-us/weather/{slug}"
    print(f"\n🌦️ Hämtar MSN (EN) för {city.title()}: {url}")
    res = requests.get(url)
    try:
        res.raise_for_status()
    except requests.HTTPError as e:
        print(f"⚠️ Misslyckades med {res.status_code} för {city}: {e}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if not tag or not tag.string:
        print(f"⚠️ __NEXT_DATA__ inte hittad för {city}, skippar")
        return None

    data = json.loads(tag.string)
    hourly = (
        data
        .get("props", {})
        .get("pageProps", {})
        .get("forecasts", {})
        .get("hourly", [])
    )
    if not isinstance(hourly, list):
        print(f"⚠️ Ingen tim-lista i JSON för {city}, skippar")
        return None

    out = []
    for h in hourly:
        iso = h.get("dateTime")
        if not iso:
            continue
        dt = datetime.fromisoformat(iso)
        out.append({
            "time": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "temp": h.get("temperature"),
            "desc": h.get("iconPhrase", "").lower()
        })

    return out

if __name__ == "__main__":
    for city in cities:
        result = fetch_and_parse(city)
        if not result:
            continue
        path = os.path.join(OUTPUT_FOLDER, f"msn_{city}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ Sparat: {path} ({len(result)} rader)")
