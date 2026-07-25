import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

from config import API_KEY, CITIES, HISTORY_URL, RAW_DIR

WINDOW_DAYS = 7


def daterange_windows(start: datetime, end: datetime, days: int):
    current = start
    while current < end:
        window_end = min(current + timedelta(days=days), end)
        yield current, window_end
        current = window_end


def fetch_history(lat: float, lon: float, start: datetime, end: datetime) -> dict:
    params = {
        "lat": lat,
        "lon": lon,
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
        "appid": API_KEY,
    }
    resp = requests.get(HISTORY_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def save_raw(city_name: str, start: datetime, end: datetime, payload: dict) -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    safe_city = city_name.replace(" ", "_")
    fname = f"{safe_city}_backfill_{start:%Y%m%d}_{end:%Y%m%d}.json"
    filepath = os.path.join(RAW_DIR, fname)

    record = {
        "city": city_name,
        "window_start_utc": start.isoformat(),
        "window_end_utc": end.isoformat(),
        "source": "openweathermap_air_pollution_history",
        "raw_response": payload,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return filepath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", type=int, default=3, help="Profondeur de backfill en mois")
    parser.add_argument("--sleep", type=float, default=1.0, help="Pause en secondes entre appels API")
    args = parser.parse_args()

    if not API_KEY:
        print("ERREUR: variable d'environnement OWM_API_KEY manquante.", file=sys.stderr)
        sys.exit(1)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30 * args.months)

    for city_name, (lat, lon, country) in CITIES.items():
        for win_start, win_end in daterange_windows(start, end, WINDOW_DAYS):
            try:
                payload = fetch_history(lat, lon, win_start, win_end)
                path = save_raw(city_name, win_start, win_end, payload)
                print(f"[OK] {city_name} {win_start:%Y-%m-%d} -> {win_end:%Y-%m-%d} : {path}")
            except Exception as e:
                print(f"[ERREUR] {city_name} {win_start:%Y-%m-%d}: {e}", file=sys.stderr)
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
