import requests
import json
import os
from datetime import datetime

# Hämta API-nyckel från miljövariabel/secrets
API_KEY = os.environ.get("WEATHERAPI_KEY")
if not API_KEY:
    raise ValueError("❌ Saknar API-nyckel – lägg till WEATHERAPI_KEY som secret eller miljövariabel.")

# Lista över orter
cities = [
    "eskilstuna",
    "stockholm",
    "göteborg",
    "lomma",
    "malmö",
    "umeå"
]

# Mappar
OUTPUT_FOLDER = "data"
RAW_FOLDER = os.path.join(OUTPUT_FOLDER, "raw")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(RAW_FOLDER, exist_ok=True)

# Hämta hourly forecast
for city in cities:
    print(f"\n🌦️ Hämtar WeatherAPI-data för {city.title()}...")

    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city},SE&lang=sv&days=2&aqi=no&alerts=no"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Spara rådata
        raw_path = os.path.join(RAW_FOLDER, f"weatherapi_{city}.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"📄 Rådata sparad: {raw_path}")

        # Extrahera hourly-data
        hourly = []
        for day in data["forecast"]["forecastday"]:
            for hour in day["hour"]:
                time_str = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
                temp = round(hour["temp_c"], 1)
                desc = hour["condition"]["text"].lower()

                hourly.append({
                    "time": time_str,
                    "temp": temp,
                    "desc": desc
                })

        # Spara förenklad hourly-data i rätt format
        output_path = os.path.join(OUTPUT_FOLDER, f"weatherapi_{city}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(hourly, f, indent=2, ensure_ascii=False)
        print(f"✅ Hourly-data sparad: {output_path}")

    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")
