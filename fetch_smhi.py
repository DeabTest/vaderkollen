import requests
import json
import os
import time

# Lista över orter
cities = [
    "eskilstuna",
    "stockholm",
    "göteborg",
    "lomma",
    "malmö",
    "umeå"
]

OUTPUT_FOLDER = "data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Hämta koordinater
def get_coordinates(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name + ", Sweden",
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "ai-vader-test (kontakt@example.com)"  # <-- byt gärna ut
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
        else:
            return None, None
    except Exception as e:
        print(f"❌ Kunde inte hämta koordinater för {city_name}: {e}")
        return None, None

# Hämta SMHI-data
def fetch_smhi_forecast(lat, lon, city):
    url = f"https://opendata.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    print(f"🔗 URL för {city}: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Kontrollera om svaret faktiskt innehåller JSON
        if response.text.strip() == "":
            raise ValueError("Tomt svar från SMHI")
        return response.json()
    except Exception as e:
        print(f"❌ Fel vid API-anrop för {city}: {e}")
        print(f"📄 SMHI-svar: {response.text}")
        return None

# Loopa över städer
for city in cities:
    print(f"\n🌦️ Hämtar SMHI-prognos för {city.title()}...")

    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        print(f"❌ Kunde inte hitta koordinater för {city}")
        continue

    data = fetch_smhi_forecast(lat, lon, city)
    if data:
        output_path = os.path.join(OUTPUT_FOLDER, f"{city}_smhi.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Sparad till {output_path}")
    else:
        print(f"⚠️ Inget data sparat för {city}")

    time.sleep(1)  # Undvik att överbelasta SMHI
