import requests
import json
import os

# 🧩 Steg 1: Inställningar
API_KEY = "1c38e00bc35998299133d067befd75a5"  # <-- byt ut mot din egen nyckel
CITY_NAME = "Eskilstuna"
COUNTRY_CODE = "SE"
OUTPUT_FOLDER = "data"
OUTPUT_FILE = f"{OUTPUT_FOLDER}/{CITY_NAME.lower()}.json"

# 🧩 Steg 2: Bygg URL
url = (
    "https://api.openweathermap.org/data/2.5/forecast"
    f"?q={CITY_NAME},{COUNTRY_CODE}&appid={API_KEY}&units=metric&lang=sv"
)

# 🧩 Steg 3: Hämta data
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    # Skapa mapp om den inte finns
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Spara datan till fil
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Prognos sparad som '{OUTPUT_FILE}'")
else:
    print(f"❌ Fel vid API-anrop: {response.status_code}")
    print(response.text)
