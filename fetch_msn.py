#!/usr/bin/env python3
import requests
import json
import os
import unicodedata
from datetime import datetime
from bs4 import BeautifulSoup

# Lista över orter
cities = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

OUTPUT_FOLDER = "data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def slugify(city):
    """Ta bort diakritiska tecken åäö → aao osv, för engelsk fallback."""
    nfkd = unicodedata.normalize("NFKD", city)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

def find_swedish_url(en_html):
    """Hitta <link rel="alternate" hreflang="sv-se"> i engelsk sida."""
    soup = BeautifulSoup(en_html, "html.parser")
    tag = soup.find("link", {"rel": "alternate", "hreflang": "sv-se"})
    return tag["href"] if tag and tag.has_attr("href") else None

def fetch_msn_html(city):
    """Hämta HTML från svenska MSN om möjligt, annars engelsk sida."""
    slug = slugify(city)
    en_url = f"https://www.msn.com/en-us/weather/{slug}"
    print(f"🌦️ Hämtar engelska MSN för {city}: {en_url}")
    r = requests.get(en_url)
    if r.status_code != 200:
        print(f"⚠️ Engelska sidan gav {r.status_code}, hoppar över")
        return None

    sv_url = find_swedish_url(r.text)
    if sv_url:
        print(f"🌦️ Byter till svenska MSN-URL: {sv_url}")
        r2 = requests.get(sv_url)
        if r2.status_code == 200:
            return r2.text
        print(f"⚠️ Svenska sidan gav {r2.status_code}, använder engelska")
    return r.text

def parse_and_save(city, html):
    soup = BeautifulSoup(html, "html.parser")
    # Loopar alla script[type=application/json] och söker efter "forecasts"
    scripts = soup.find_all("script", {"type": "application/json"})
    js = None
    for tag in scripts:
        txt = tag.string or ""
        if '"forecasts"' in txt:
            try:
                js = json.loads(txt)
                break
            except json.JSONDecodeError:
                continue

    if not js:
        print(f"⚠️ Hittade ingen forecasts‐JSON för {city}, skippar.")
        return

    # Extrahera tim‐lista
    hourly = (
        js.get("props", {})
          .get("pageProps", {})
          .get("forecasts", {})
          .get("hourly", None)
        or js.get("forecasts", {}).get("hourly", [])
    )
    if not isinstance(hourly, list):
        print(f"⚠️ Ingen hourly‐lista för {city}, skippar.")
        return

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

    path = os.path.join(OUTPUT_FOLDER, f"msn_{city}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✅ Sparat: {path} ({len(out)} datapunkter)")

if __name__ == "__main__":
    for city in cities:
        html = fetch_msn_html(city)
        if html:
            parse_and_save(city, html)
