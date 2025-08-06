import json
import os
import statistics

# Lista över orter
locations = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

# Karta över källa och motsvarande filprefix
source_filenames = {
    "openweather": "{location}.json",
    "smhi": "weather_smhi_{location}.json",  # Ändrat här
    "yr": "{location}_yr.json",
    "weatherapi": "{location}_weatherapi.json",
}

# Funktion för att läsa väderdata från en viss källa
def read_source_data(source, location):
    filename = source_filenames[source].format(location=location)
    path = f"data/{filename}"
    if not os.path.exists(path):
        print(f"⚠️ Saknar fil: {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {entry["time"]: entry for entry in data if "time" in entry}
            else:
                print(f"⚠️ Filen {path} innehåller inte en lista.")
                return None
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

# Samlar alla kombinerade prognoser
all_combined = {}

for location in locations:
    print(f"\n📍 Bearbetar {location.title()}...")

    source_data = {}

    for source in source_filenames:
        data = read_source_data(source, location)
        if data:
            source_data[source] = data

    if not source_data:
        print(f"⛔ Ingen data tillgänglig för {location}")
        continue

    all_times = [set(d.keys()) for d in source_data.values()]
    common_times = set.intersection(*all_times)

    if not common_times:
        print(f"⚠️ Inga gemensamma tidpunkter för {location}")
        continue

    combined = []

    for time in sorted(common_times):
        entries = []

        for source, data in source_data.items():
            entry = data.get(time)
            if entry and "temp" in entry and "desc" in entry:
                entries.append({
                    "temp": entry["temp"],
                    "desc": entry["desc"],
                    "source": source
                })

        if entries:
            all_descs = [e["desc"] for e in entries]
            most_common_desc = max(set(all_descs), key=all_descs.count)

            matching_entries = [e for e in entries if e["desc"] == most_common_desc]
            temps = [e["temp"] for e in matching_entries]
            used_sources = [e["source"] for e in matching_entries]

            avg_temp = round(sum(temps) / len(temps), 1)
            reliability = calculate_reliability(temps)

            combined.append({
                "time": time,
                "avg_temp": avg_temp,
                "desc": most_common_desc,
                "reliability": reliability,
                "sources_used": used_sources
            })

    output_path = f"data/combined_{location}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"✅ Sparat: {output_path}")

    all_combined[location] = combined

# Spara samlad fil för alla orter
with open("data/combined.json", "w", encoding="utf-8") as f:
    json.dump(all_combined, f, indent=2, ensure_ascii=False)
print("\n📦 Samlad fil sparad: data/combined.json")
