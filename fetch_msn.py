import requests, json, os
from bs4 import BeautifulSoup
from datetime import datetime

cities = ["eskilstuna", "stockholm", "göteborg", "lomma", "malmö", "umeå"]
OUTPUT = "data"
os.makedirs(OUTPUT, exist_ok=True)

for city in cities:
    url = f"https://www.msn.com/sv-se/väder/{city}"
    print(f"🌦️ Hämtar MSN Väder för {city.title()} ({url})")
    res = requests.get(url)
    res.raise_for_status()

    # Extrahera JSON från <script id="__NEXT_DATA__">
    soup = BeautifulSoup(res.text, "html.parser")
    tag = soup.find("script", {"id": "__NEXT_DATA__"})
    data = json.loads(tag.string)

    # I Next-data finns prognoser under props.pageProps.forecasts.hourly
    hourly = data["props"]["pageProps"]["forecasts"]["hourly"]

    out = []
    for h in hourly:
        # h innehåller t.ex. 'dateTime': "2025-08-07T15:00:00"
        dt = datetime.fromisoformat(h["dateTime"])
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        temp = h.get("temperature")
        desc = h.get("iconPhrase", "").lower()  # t.ex. "Partly cloudy"
        out.append({"time": time_str, "temp": temp, "desc": desc})

    path = os.path.join(OUTPUT, f"msn_{city}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"✅ Sparat: {path}")
