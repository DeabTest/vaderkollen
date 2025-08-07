#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

# Mappning stad → MSN:s svenska prognos-URL
MSN_URLS = {
    "eskilstuna": "https://www.msn.com/sv-se/vader/prognos/in-Eskilstuna,Sodermanland-County",
    # Lägg till övriga städer här:
    # "stockholm":  "https://www.msn.com/sv-se/vader/prognos/in-Stockholm,Stockholms-län-County",
    # "göteborg":   "https://www.msn.com/sv-se/vader/prognos/in-Göteborg,Västra-Götalands-län-County",
    # "lomma":      "https://www.msn.com/sv-se/vader/prognos/in-Lomma,Skåne-län-County",
    # "malmö":      "https://www.msn.com/sv-se/vader/prognos/in-Malmö,Skåne-län-County",
    # "umeå":       "https://www.msn.com/sv-se/vader/prognos/in-Umeå,Västernorrlands-län-County",
}

# Engelska fallback‐URL om svensk saknas
EN_URL_TEMPLATE = "https://www.msn.com/en-us/weather/{slug}"

# Lista över orter
cities = list(MSN_URLS.keys())

OUTPUT_FOLDER = "data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def slugify(city):
    """Enkel slugifiering för engelska fallback-URL."""
    return city.lower().replace("å", "a").replace("ä", "a").replace("ö", "o")

def fetch_html(city):
    # Först: använd den svenska URL:en om vi har en
    url = MSN_URLS.get(city)
    if url:
        print(f"🌦️ Hämtar svenska MSN-prognos för {city}: {url}")
        res = requests.get(url)
        if res.status_code == 404:
            print(f"⚠️ 404 på svensk URL, försöker engelska...")
        else:
            res.raise_for_status()
            return res.text

    # Fallback: engelska versionen
    slug = slugify(city)
    en_url = EN_URL_TEMPLATE.format(slug=slug)
    print(f"🌦️ Hämtar engelska MSN-prognos för {city}: {en_url}")
    res = requests.get(en_url)
    if res.status_code == 404:
        print(f"❌ Ingen giltig MSN-sida för {city} (404 på både SV & EN)")
        return None
    res.raise_for_status()
    return res.text

def parse_and_save(city, html):
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if not tag or not tag.string:
        print(f"⚠️ Ingen __NEXT_DATA__ JSON för {city}, skippar.")
        return

    data = json.loads(tag.string)
    hourly = (data.get("props", {})
                  .get("pageProps", {})
                  .get("forecasts", {})
                  .get("hourly", []))
    if not hourly:
        print(f"⚠️ Ingen timdata i JSON för {city}, skippar.")
        return

    out = []
    for h in hourly:
        iso = h.get("dateTime")
        if not iso:
            continue
        dt = datetime.fromisoformat(iso)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        out.append({
            "time": time_str,
            "temp": h.get("temperature"),
            "desc": h.get("iconPhrase", "").lower()
        })

    path = os.path.join(OUTPUT_FOLDER, f"msn_{city}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"✅ Sparat: {path} ({len(out)} datapunkter)")

if __name__ == "__main__":
    for city in cities:
        html = fetch_html(city)
        if html:
            parse_and_save(city, html)
