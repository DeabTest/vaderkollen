import json
import os
import statistics

# Lista med orter
locations = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

# Karta över källa och motsvarande filprefix
source_filenames = {
    "openweather": "{location}.json",
    "smhi": "smhi_{location}.json",
    "yr": "{location}_yr.json"
    "weatherapi": "{location}_weatherapi.json"
}

# Funktion för att läsa väderdata från en viss källa
def read_source_data(source, location):
    filename = source_filenames[source].format(location=location)
    path = f"data/{filename}"
    if not os.path.exists(path):
        print(f"⚠️ Saknar fil: {path}")
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Fel vid läsning av {path}: {e}")
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

# Lista som samlar alla kombinerade prognoser
all_combined = []

# Bearbeta varje ort
for location in locations:
    temps = []
    descriptions = []
    used_sources = []

    print(f"\n🔍 Bearbetar {location.title()}...")

    for source in source_filenames:
        data = read_source_data(source, location)

        if data and isinstance(data, dict):
            if "temp" in data and "desc" in data:
                temps.append(data["temp"])
                descriptions.append(data["desc"])
                used_sources.append(source)
            else:
                print(f"⚠️ Fil för {source} och {location} saknar 'temp' eller 'desc'")
        else:
            print(f"⚠️ Ingen användbar data från källa {source} för {location}")

    if temps:
        avg_temp = round(sum(temps) / len(temps), 1)
        most_common_desc = max(set(descriptions), key=descriptions.count)
        reliability = calculate_reliability(temps)

        result = {
            "location": location.capitalize(),
            "avg_temp": avg_temp,
            "desc": most_common_desc,
            "reliability": reliability,
            "sources_used": used_sources,
        }

        with open(f"data/combined_{location}.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"✅ Kombinerad prognos sparad: data/combined_{location}.json")

        all_combined.append(result)
    else:
        print(f"⛔ Ingen tillräcklig data för {location}, hoppar över.")

# Spara samlad fil med alla orter
if all_combined:
    with open("data/combined.json", "w") as f:
        json.dump(all_combined, f, indent=2)
    print("\n📦 Samlad fil skapad: data/combined.json")
else:
    print("\n❌ Ingen kombinerad data kunde sparas – kontrollera datakällorna.")
