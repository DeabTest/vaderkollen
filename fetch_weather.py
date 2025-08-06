import requests
import json
import os

# Hämta API-nyckel från GitHub Secret (eller miljövariabel)
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

# Skapa mapp om den inte finns
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Loopa igenom orterna
for city in cities:
    print(f"Hämtar väder för {city.title()}...")

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city},{COUNTRY_CODE}&appid={API_KEY}&units=metric&lang=sv"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        output_path = os.path.join(OUTPUT_FOLDER, f"{city}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Sparad till {output_path}")

    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")
