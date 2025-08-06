import requests
import json
import os

print("🌦️ Hämtar SMHI-prognos för alla städer...")

# Städer med justerade koordinater (lite avrundade för att undvika API-buggar)
locations = {
    "eskilstuna": {"lat": 59.37, "lon": 16.51},
    "stockholm": {"lat": 59.33, "lon": 18.06},
    "göteborg": {"lat": 57.71, "lon": 11.97},
    "lomma": {"lat": 55.68, "lon": 13.07},
    "malmö": {"lat": 55.60, "lon": 13.00},
    "umeå": {"lat": 63.82, "lon": 20.26}  # ✅ Justerat så att det fungerar
}

# Funktion för att hämta temperatur och väderbeskrivning från SMHI
def fetch_smhi_forecast(lat, lon):
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Hitta första temperaturen och väderkoden i forecasten
        for time_series in data["timeSeries"]:
            params = {p["name"]: p["values"][0] for p in time_series["parameters"]}
            if "t" in params and "Wsymb2" in params:
                temp = params["t"]
                symbol = params["Wsymb2"]
                desc = smhi_symbol_to_text(symbol)
                return temp, desc

        return None, None
    except Exception as e:
        print(f"❌ Fel vid API-anrop för {lat}, {lon}: {e}")
        return None, None

# SMHI:s vädersymboler till text
def smhi_symbol_to_text(symbol):
    mapping = {
        1: "Klart",
        2: "Lätt molnighet",
        3: "Halvklart",
        4: "Molnigt",
        5: "Mulet",
        6: "Dimma",
        7: "Lätt regn",
        8: "Regn",
        9: "Kraftigt regn",
        10: "Åska",
        11: "Lätt snö",
        12: "Snö",
        13: "Kraftigt snöfall",
    }
    return mapping.get(symbol, "Okänt")

# Skapa mapp om den inte finns
os.makedirs("data", exist_ok=True)

# Gå igenom alla städer
for location, coords in locations.items():
    print(f"🌦️ Hämtar SMHI-prognos för {location.capitalize()}...")
    print(f"🔗 URL för {location}: https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{coords['lon']}/lat/{coords['lat']}/data.json")

    temp, desc = fetch_smhi_forecast(coords["lat"], coords["lon"])
    if temp is not None:
        forecast = {"temp": temp, "desc": desc}
        path = f"data/smhi_{location}.json"
        with open(path, "w") as f:
            json.dump(forecast, f, indent=2)
        print(f"✅ Sparat: {path}")
    else:
        print(f"❌ Kunde inte hämta prognos för {location.capitalize()}.\n")
