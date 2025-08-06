import requests
import json
import os

print("🌦️ Hämtar SMHI-prognos för alla städer...")

# Städer med justerade koordinater
locations = {
    "eskilstuna": {"lat": 59.37, "lon": 16.51},
    "stockholm": {"lat": 59.33, "lon": 18.06},
    "göteborg": {"lat": 57.71, "lon": 11.97},
    "lomma": {"lat": 55.68, "lon": 13.07},
    "malmö": {"lat": 55.60, "lon": 13.00},
    "umeå": {"lat": 63.82, "lon": 20.26}
}

# Vädersymboler till text
def smhi_symbol_to_text(symbol):
    mapping = {
        1: "klart",
        2: "lätt molnighet",
        3: "halvklart",
        4: "molnigt",
        5: "mulet",
        6: "dimma",
        7: "lätt regn",
        8: "regn",
        9: "kraftigt regn",
        10: "åska",
        11: "lätt snö",
        12: "snö",
        13: "kraftigt snöfall",
    }
    return mapping.get(symbol, None)

# Skapa mappar
os.makedirs("data", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

# Hämta SMHI-prognos
def fetch_smhi_forecast(lat, lon):
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Spara första tre tidpunkter som rådata
        raw_path = f"data/raw/smhi_{lat}_{lon}.json"
        with open(raw_path, "w") as f:
            json.dump(data["timeSeries"][:3], f, indent=2)
        print(f"📄 Rådata sparad: {raw_path}")

        # Extrahera första tillgängliga temp och symbol
        for time_series in data["timeSeries"]:
            params = {p["name"]: p["values"][0] for p in time_series["parameters"]}
            if "t" in params and "Wsymb2" in params:
                temp = round(params["t"], 1)
                symbol = params["Wsymb2"]
                desc = smhi_symbol_to_text(symbol)
                return temp, desc

        return None, None
    except Exception as e:
        print(f"❌ Fel vid API-anrop för {lat}, {lon}: {e}")
        return None, None

# Kör för varje stad
for location, coords in locations.items():
    print(f"\n🌦️ Hämtar SMHI-prognos för {location.capitalize()}...")

    lat, lon = coords["lat"], coords["lon"]
    temp, desc = fetch_smhi_forecast(lat, lon)

    if temp is not None:
        forecast = {"temp": temp}
        if desc:  # Lägg bara till desc om den är giltig
            forecast["desc"] = desc

        path = f"data/smhi_{location}.json"
        with open(path, "w") as f:
            json.dump(forecast, f, indent=2)
        print(f"✅ Sparat: {path}")
    else:
        print(f"❌ Kunde inte hämta giltig prognos för {location.capitalize()}.")
