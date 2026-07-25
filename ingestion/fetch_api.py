import json
import os
import sys
from datetime import datetime, timezone

import requests

from config import API_KEY, CITIES, CURRENT_URL, RAW_DIR


def fetch_current(city_name: str, lat: float, lon: float) -> dict:
    params = {"lat": lat, "lon": lon, "appid": API_KEY}
    resp = requests.get(CURRENT_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def save_raw(city_name: str, payload: dict) -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_city = city_name.replace(" ", "_")
    filename = f"{safe_city}_{ts}.json"
    filepath = os.path.join(RAW_DIR, filename)

    record = {
        "city": city_name,
        "fetched_at_utc": ts,
        "source": "openweathermap_air_pollution_current",
        "raw_response": payload,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return filepath


def main():
    if not API_KEY:
        print("ERREUR: Missing OWM_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    for city_name, (lat, lon, country) in CITIES.items():
        try:
            payload = fetch_current(city_name, lat, lon)
            path = save_raw(city_name, payload)
            print(f"[OK] {city_name} -> {path}")
        except Exception as e:
            # On logue l'erreur mais on continue les autres villes.
            print(f"[ERREUR] {city_name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
