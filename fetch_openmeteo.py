#!/usr/bin/env python3
import requests
import json
import os
import time
from datetime import datetime
from urllib.parse import urlencode

# Lista över orter
cities = [
    "eskilstuna",
    "stockholm",
    "göteborg",
    "lomma",
    "malmö",
    "umeå"
]

# Hjälpfunktion för Nominatim-geokodning
def get_coordinates(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name + ", Sweden",
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "ai-vader-bot (kontakt@example.com)"}
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    results = r.json()
    if results:
        return float(results[0]["lat"]), float(results[0]["lon"])
    else:
        return None, None

# Mapping från Open-Meteo weathercode → beskrivning på svenska
WEATHERCODE_MAP = {
    0:  "klar himmel",
    1:  "nästan klar himmel",
    2:  "halvklart",
    3:  "mulet",
    45: "dimma",
    48: "rimdimma",
    51: "lätt duggregn",
    53: "måttligt duggregn",
    55: "täta duggregnskurar",
    56: "lätta snöblandade duggregn",
    57: "täta snöblandade regnskurar",
    61: "lätt regn",
    63: "måttligt regn",
    65: "kraftigt regn",
    66: "lätt snöblandat regn",
    67: "kraftigt snöblandat regn",
    71: "lätt snöfall",
    73: "måttligt snöfall",
    75: "kraftigt snöfall",
    77: "snöflingor i drivor",
    80: "lätta regnskurar",
    81: "måttliga regnskurar",
    82: "kraftiga regnskurar",
    85: "lätta snöskurar",
    86: "kraftiga snöskurar",
    95: "åska",
    96: "svag åska",
    99: "kraftig åska",
}

OUTPUT_FOLDER = "data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for city in cities:
    print(f"\n🌦️ Hämtar Open-Meteo-data för {city.title()}…")
    lat, lon = get_coordinates(city)
    if lat is None:
        print(f"❌ Kunde inte geokoda {city}")
        continue

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,weathercode",
        "timezone": "Europe/Stockholm"
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")
        continue

    times = data.get("hourly", {}).get("time", [])
    temps = data.get("hourly", {}).get("temperature_2m", [])
    codes = data.get("hourly", {}).get("weathercode", [])

    hourly = []
    for t, temp, code in zip(times, temps, codes):
        # t är en ISO-tid med 'T', ex "2025-08-07T15:00"
        dt = datetime.fromisoformat(t)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        desc = WEATHERCODE_MAP.get(code, "okänt väder")
        hourly.append({
            "time": time_str,
            "temp": round(temp, 1),
            "desc": desc
        })

    out_path = os.path.join(OUTPUT_FOLDER, f"openmeteo_{city}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(hourly, f, ensure_ascii=False, indent=2)
    print(f"✅ Sparat: {out_path} ({len(hourly)} poster)")
    time.sleep(1)  # skona Nominatim
