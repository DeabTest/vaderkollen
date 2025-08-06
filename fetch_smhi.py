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

# Skapa mapp om den inte finns
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Funktion för att hämta koordinater med OpenStreetMap (Nominatim)
def get_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name + ", Sweden",
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "ai-vader-test (kontakt@example.com)"  # <-- byt till din e-post om du vill
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    results = response.json()
    if results:
        return float(results[0]["lat"]), float(results[0]["lon"])
    else:
        return None, None

# Funktion för att hämta SMHI-prognos
def fetch_smhi_forecast(lat, lon):
    url = f"https://opendata.smhi.se/apidocs/metfcst/parameters.html"
    url = f"https://opendata.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Loopa över alla orter
for city in cities:
    print(f"Hämtar SMHI-prognos för {city.title()}...")

    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        print(f"❌ Kunde inte hitta koordinater för {city}")
        continue

    try:
        data = fetch_smhi_forecast(lat, lon)
        output_path = os.path.join(OUTPUT_FOLDER, f"{city}_smhi.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Sparad till {output_path}")
    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")

    # SMHI gillar inte spam – sov lite mellan anropen
    time.sleep(1)
