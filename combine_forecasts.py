import json
import os
import statistics
from collections import Counter
from datetime import datetime

# Lista över orter
locations = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

# Karta över källa och motsvarande filprefix
source_filenames = {
    "openweather": "{location}.json",
    "smhi": "weather_smhi_{location}.json",
    "yr": "{location}_yr.json",
    "weatherapi": "{location}_weatherapi.json",
}

# Funktion för att normalisera tidsformat
def normalize_time(time_str):
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    print(f"⚠️ Okänt tidsformat: {time_str}")
    return time_str

# Funktion för att läsa väderdata från en viss källa
def read_source_data(source, location):
    filename = source_filenames[source].format(location=location)
    path = f"data/{filename}"
    if not os.path.exists(path):
        print(f"⚠️ Saknar fil: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        entries = []

        # Om list (OpenWeather, SMHI, WeatherAPI)
        if isinstance(raw, list):
            for e in raw:
                if "time" in e and "temp" in e and "desc" in e:
                    entries.append({
                        "time": normalize_time(e["time"]),
                        "temp": e["temp"],
                        "desc": e["desc"]
                    })

        # Om dict (YR): nyckel = datum, värde = lista av timvärden
        elif isinstance(raw, dict) and source == "yr":
            for date_key, hours in raw.items():
                for h in hours:
                    # h["time"] är t.ex. "03:00"
                    full_time = f"{date_key} {h['time']}"
                    entries.append({
                        "time": normalize_time(full_time),
                        "temp": h.get("temp"),
                        "desc": h.get("desc")
                    })

        else:
            print(f"⚠️ Filen {path} innehåller inte en lista eller YR-format.")
            return None

        # Byt till dict med time som nyckel
        return { e["time"]: e for e in entries }

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

    # Hitta tidpunkter som finns i minst två källor
    time_counts = Counter()
    for d in source_data.values():
        time_counts.update(d.keys())
    common_times = [t for t, cnt in time_counts.items() if cnt >= 2]

    if not common_times:
        print(f"⚠️ Inga gemensamma tidpunkter för {location}")
        continue

    combined = []
    for time in sorted(common_times):
        entries = []
        for src, d in source_data.items():
            e = d.get(time)
            if e:
                entries.append({"temp": e["temp"], "desc": e["desc"], "source": src})

        temps = [e["temp"] for e in entries]
        descs = [e["desc"] for e in entries]
        sources = [e["source"] for e in entries]

        most_common_desc = Counter(descs).most_common(1)[0][0]
        avg_temp = round(sum(temps) / len(temps), 1)
        reliability = calculate_reliability(temps)

        combined.append({
            "time": time,
            "avg_temp": avg_temp,
            "desc": most_common_desc,
            "reliability": reliability,
            "sources_used": sources
        })

    # Spara per ort
    out_path = f"data/combined_{location}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"✅ Sparat: {out_path}")

    all_combined[location] = combined

# Spara samlad fil för alla orter
with open("data/combined.json", "w", encoding="utf-8") as f:
    json.dump(all_combined, f, indent=2, ensure_ascii=False)
print("\n📦 Samlad fil sparad: data/combined.json")
