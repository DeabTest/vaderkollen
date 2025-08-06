import json
import os
import statistics

# Lista med orter
locations = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

# Funktion för att läsa väderdata från en viss källa
def read_source_data(source, location):
    path = f"data/{source}_{location}.json"
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fel vid läsning av {path}: {e}")
        return None

# Funktion för att räkna ut tillförlitlighet
def calculate_reliability(temps):
    if len(temps) < 2:
        return "låg"
    spread = max(temps) - min(temps)
    stdev = statistics.stdev(temps)
    if spread < 1 and stdev < 0.5:
        return "hög"
    elif spread < 3 and stdev < 1.5:
        return "medel"
    else:
        return "låg"

# Bearbeta varje ort
for location in locations:
    temps = []
    descriptions = []
    sources = ["openweather", "smhi", "yr"]

    for source in sources:
        data = read_source_data(source, location)
        if data and "temp" in data:
            temps.append(data["temp"])
            descriptions.append(data["desc"])

    if temps:
        avg_temp = round(sum(temps) / len(temps), 1)
        most_common_desc = max(set(descriptions), key=descriptions.count)
        reliability = calculate_reliability(temps)

        result = {
            "location": location.capitalize(),
            "avg_temp": avg_temp,
            "desc": most_common_desc,
            "reliability": reliability,
            "sources_used": len(temps),
        }

        with open(f"data/combined_{location}.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"Kombinerad prognos sparad: data/combined_{location}.json")

    else:
        print(f"Ingen data tillgänglig för {location}, hoppar över.")
