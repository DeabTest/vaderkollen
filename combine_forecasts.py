import json
import os
from collections import Counter
from datetime import datetime

cities = [
    "eskilstuna",
    "stockholm",
    "göteborg",
    "lomma",
    "malmö",
    "umeå"
]

def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def round_hour(timestamp):
    return timestamp[:13] + ":00:00"

for city in cities:
    print(f"Sammanställer prognos för {city.title()}...")

    owm = load_json(f"data/{city}_openweather.json")
    smhi = load_json(f"data/{city}_smhi.json")
    yr = load_json(f"data/{city}_yr.json")

    if not owm or not smhi or not yr:
        print(f"❌ Saknar data för {city}, hoppar över.")
        continue

    # --- OpenWeatherMap ---
    owm_forecast = {}
    for item in owm["list"]:
        timestamp = round_hour(item["dt_txt"])
        temp = item["main"]["temp"]
        desc = item["weather"][0]["description"]
        owm_forecast[timestamp] = {"temp": temp, "desc": desc}

    # --- SMHI ---
    smhi_forecast = {}
    for t in smhi["timeSeries"]:
        timestamp = t["validTime"]
        timestamp = round_hour(timestamp)
        temp = next((p["values"][0] for p in t["parameters"] if p["name"] == "t"), None)
        if temp is not None:
            smhi_forecast[timestamp] = {"temp": temp, "desc": "okänt"}  # SMHI har inte textbeskrivning

    # --- Yr ---
    yr_forecast = {}
    for t in yr["properties"]["timeseries"]:
        timestamp = round_hour(t["time"])
        temp = t["data"]["instant"]["details"].get("air_temperature")
        desc = t["data"].get("next_1_hours", {}).get("summary", {}).get("symbol_code", "okänt")
        if temp is not None:
            yr_forecast[timestamp] = {"temp": temp, "desc": desc.replace("_", " ")}

    # --- Kombinera ---
    common_times = set(owm_forecast) & set(smhi_forecast) & set(yr_forecast)
    combined = []

    for timestamp in sorted(common_times):
        temps = [
            owm_forecast[timestamp]["temp"],
            smhi_forecast[timestamp]["temp"],
            yr_forecast[timestamp]["temp"]
        ]
        descs = [
            owm_forecast[timestamp]["desc"],
            yr_forecast[timestamp]["desc"]
        ]  # SMHI har ej desc

        avg_temp = round(sum(temps) / len(temps), 1)
        common_desc = Counter(descs).most_common(1)[0][0]

        combined.append({
            "time": timestamp,
            "temp": avg_temp,
            "desc": common_desc
        })

    output_path = f"data/{city}_combined.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"✅ Skapad: {output_path}")
