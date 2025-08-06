import requests
import json
import os
from datetime import datetime

# Hämta API-nyckel från miljövariabel
API_KEY = os.environ.get("OWM_API_KEY")

# Lista över orter att hämta väder för
cities = [
    "eskilstuna",
    "stockholm",
    "göteborg",
    "lomma",
    "malmö",
    "umeå"
]

# Inställningar
COUNTRY_CODE = "SE"
OUTPUT_FOLDER = "data"
RAW_FOLDER = os.path.join(OUTPUT_FOLDER, "raw")

# Skapa mappar om de inte finns
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(RAW_FOLDER, exist_ok=True)

# Loopa igenom orterna
for city in cities:
    print(f"\n🌦️ Hämtar väder för {city.title()}...")

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city},{COUNTRY_CODE}&appid={API_KEY}&units=metric&lang=sv"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Spara RÅDATA (för felsökning)
        raw_output_path = os.path.join(RAW_FOLDER, f"{city}.json")
        with open(raw_output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"📄 Rådata sparad: {raw_output_path}")

        # Extrahera hourly-data i standardformat
        hourly_data = []
        for entry in data["list"]:
            hourly_data.append({
                "time": entry["dt_txt"],
                "temp": round(entry["main"]["temp"], 1),
                "desc": entry["weather"][0]["description"]
            })

        # Spara i rätt format som t.ex. data/eskilstuna.json
        output_path = os.path.join(OUTPUT_FOLDER, f"{city}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(hourly_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Hourly-data sparad: {output_path}")

    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")
