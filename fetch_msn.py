import requests
import json
import os
import unicodedata
from datetime import datetime

# Lista över orter
cities = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

OUTPUT_FOLDER = "data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def slugify(city):
    # Ta bort accenttecken åäö → aao, etc.
    nfkd = unicodedata.normalize("NFKD", city)
    ascii_only = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return ascii_only.lower()

for city in cities:
    slug = slugify(city)
    url = f"https://www.msn.com/sv-se/väder/{slug}"
    print(f"\n🌦️ Hämtar MSN Väder för {city.title()} ({url})")

    try:
        res = requests.get(url)
        if res.status_code == 404:
            print(f"⚠️ Sida inte funnen för {city} ({url}), hoppar över.")
            continue
        res.raise_for_status()

        # Extrahera JSON från <script id="__NEXT_DATA__">
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, "html.parser")
        tag = soup.find("script", {"id": "__NEXT_DATA__"})
        if not tag or not tag.string:
            print(f"⚠️ Ingen __NEXT_DATA__ JSON hittad på sidan för {city}, hoppar över.")
            continue

        data = json.loads(tag.string)

        # Navigera till hourly-förutsägelsen
        hourly = data.get("props", {}) \
                     .get("pageProps", {}) \
                     .get("forecasts", {}) \
                     .get("hourly", [])
        if not hourly:
            print(f"⚠️ Ingen timdata i JSON för {city}, hoppar över.")
            continue

        out = []
        for h in hourly:
            iso = h.get("dateTime")  # ex: "2025-08-07T15:00:00"
            if not iso:
                continue
            dt = datetime.fromisoformat(iso)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            temp = h.get("temperature")
            desc = h.get("iconPhrase", "").lower()
            out.append({"time": time_str, "temp": temp, "desc": desc})

        # Spara resultat
        path = os.path.join(OUTPUT_FOLDER, f"msn_{city}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"✅ Sparat: {path} ({len(out)} poster)")

    except Exception as e:
        print(f"❌ Fel vid hämtning/parsing för {city}: {e}")
