import requests
import json
import os
from datetime import datetime

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

# Kör för varje stad
for city, coords in locations.items():
    print(f"\n🌦️ Hämtar SMHI-prognos för {city.title()}...")

    lat, lon = coords["lat"], coords["lon"]
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Spara rådata
        raw_path = f"data/raw/smhi_{city}.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"📄 Rådata sparad: {raw_path}")

        hourly = []

        for time_series in data["timeSeries"]:
            valid_time = time_series["validTime"]
            params = {p["name"]: p["values"][0] for p in time_series["parameters"]}

            if "t" in params and "Wsymb2" in params:
                temp = round(params["t"], 1)
                desc = smhi_symbol_to_text(params["Wsymb2"])
                time_str = datetime.fromisoformat(valid_time).strftime("%Y-%m-%d %H:%M")

                hourly.append({
                    "time": time_str,
                    "temp": temp,
                    "desc": desc
                })

        # Spara i standardformat
        output_path = f"data/weather_smhi_{city}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(hourly, f, ensure_ascii=False, indent=2)
        print(f"✅ Hourly-data sparad: {output_path}")

    except Exception as e:
        print(f"❌ Fel vid hämtning för {city}: {e}")
