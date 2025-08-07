# För att schemalägga detta skript att köras varje timme dygnet runt,
# lägg till följande rad i din crontab (kör `crontab -e`):
#
# 0 * * * * /usr/bin/env python3 /sökväg/till/combine_forecasts.py >> /sökväg/till/combine_forecasts.log 2>&1
#
# Detta kör skriptet på minut 0 varje timme och loggar output till combine_forecasts.log.

#!/usr/bin/env python3
import json
import os
import statistics
import sys
from collections import Counter
from datetime import datetime

# Lista över orter
locations = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]

# Karta över källa och motsvarande filprefix
source_filenames = {
    "openweather": "{location}.json",
    "smhi": "weather_smhi_{location}.json",
    "yr": "{location}_yr.json",
    "weatherapi": "weatherapi_{location}.json",
    "msn":           "msn_{location}.json",
}

def normalize_time(time_str):
    """Normalisera olika tidsformat till YYYY-MM-DD HH:MM:SS."""
    for fmt in ("%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    print(f"⚠️ Okänt tidsformat: {time_str}", file=sys.stderr)
    return time_str

def read_source_data(source, location):
    """Läs och normalisera data från en källa för en viss ort."""
    filename = source_filenames[source].format(location=location)
    path = os.path.join("data", filename)
    if not os.path.exists(path):
        print(f"⚠️ Saknar fil: {path}", file=sys.stderr)
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"❌ Fel vid läsning av {path}: {e}", file=sys.stderr)
        return None

    entries = []
    if isinstance(raw, list):
        # OpenWeather, SMHI, WeatherAPI
        for e in raw:
            if "time" in e and "temp" in e and "desc" in e:
                entries.append({
                    "time": normalize_time(e["time"]),
                    "temp": e["temp"],
                    "desc": e["desc"]
                })
    elif isinstance(raw, dict) and source == "yr":
        # YR: dict av datum → lista av timvärden
        for date_key, hours in raw.items():
            for h in hours:
                t = h.get("time")
                if t is None: 
                    continue
                full_time = f"{date_key} {t}"
                entries.append({
                    "time": normalize_time(full_time),
                    "temp": h.get("temp"),
                    "desc": h.get("desc")
                })
    else:
        print(f"⚠️ Filen {path} innehåller inte en lista eller YR-format.", file=sys.stderr)
        return None

    return { e["time"]: e for e in entries }

def calculate_reliability(temps):
    """Beräkna hög/medel/låg baserat på temperaturvariation."""
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

def combine_for_location(location):
    """Kombinera prognoser för en specifik ort."""
    source_data = {}
    for source in source_filenames:
        data = read_source_data(source, location)
        if data:
            print(f"ℹ️ Läste in {len(data)} poster från {source}")
            source_data[source] = data
    if not source_data:
        print(f"⛔ Ingen data tillgänglig för {location}", file=sys.stderr)
        return

    # Hitta tidpunkter som finns i minst två källor
    time_counts = Counter()
    for d in source_data.values():
        time_counts.update(d.keys())
    common_times = sorted([t for t, cnt in time_counts.items() if cnt >= 2])

    combined = []
    for time in common_times:
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

    out_path = os.path.join("data", f"combined_{location}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"✅ Sparat: {out_path}")

def main():
    for location in locations:
        print(f"\n📍 Bearbetar {location.title()}...")
        combine_for_location(location)

    # Spara samlad fil för alla orter
    all_combined = {
        location: json.load(open(os.path.join("data", f"combined_{location}.json"), encoding="utf-8"))
        for location in locations
    }
    with open("data/combined.json", "w", encoding="utf-8") as f:
        json.dump(all_combined, f, indent=2, ensure_ascii=False)
    print("\n📦 Samlad fil sparad: data/combined.json")

if __name__ == "__main__":
    main()
