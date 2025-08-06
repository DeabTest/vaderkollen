import requests
import json
import os
import time

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

# Hämta koordinater med Nominatim
def get_coordinates(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name + ", Sweden",
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "ai-vader-bot (kontakt@example.com)"  # ← byt till din e-post om du vill
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    results = response.json()
    if results:
        return float(results[0]["lat"]), float(results[0]["lon"])
    else:
        return None, None

# Hämta Yr-prognos
def fetch_yr_forecast(lat, lon):
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    headers = {
        "User-Agent": "ai-vader-bot (kontakt@example.com)"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Kör för varje ort
for city in cities:
    print(f"Hämtar Yr-prognos för {city.title()}...")

    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        print(f"❌ Kunde inte hitta koordinater för {city}")
        continue

    try:
        data = fetch_yr_forecast(lat, lon)
        output_path = os.path.join(OUTPUT_FOLDER, f"{city}_yr.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Sparad till {output_path}")
    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")

    time.sleep(1)  # Snällt mot Nominatim
