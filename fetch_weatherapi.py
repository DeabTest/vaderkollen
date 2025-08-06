import requests
import json
import os

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

# Loopa igenom alla orter
for city in cities:
    print(f"\n🌦️ Hämtar WeatherAPI-data för {city.title()}...")

    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city},SE&lang=sv"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Spara rådata
        raw_path = os.path.join(RAW_FOLDER, f"{city}_weatherapi.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"📄 Rådata sparad: {raw_path}")

        # Extrahera förenklad väderdata
        temp = round(data["current"]["temp_c"], 1)
        desc = data["current"]["condition"]["text"].lower()

        clean_data = {
            "temp": temp,
            "desc": desc
        }

        # Spara förenklad data
        output_path = os.path.join(OUTPUT_FOLDER, f"{city}_weatherapi.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2)
        print(f"✅ Förenklad data sparad: {output_path}")

    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")
