"""
build_clean.py — Reconstruit ENTIEREMENT storage/clean/clean.csv depuis storage/raw/.
Ne modifie jamais raw/. Gère la dédup (même ville + même heure = une seule ligne)
et le tri chronologique. A relancer à chaque run du pipeline.

Contrat de données clean/ (une ligne par ville et par heure):
    city, country, latitude, longitude, timestamp_utc, aqi_owm,
    co, no, no2, o3, so2, pm2_5, pm10, nh3

Unités (OpenWeatherMap Air Pollution API):
    aqi_owm : indice qualitatif OWM 1 (bon) à 5 (très mauvais) — PAS l'AQI US 0-500
    co, no, no2, o3, so2, pm2_5, pm10, nh3 : concentrations en µg/m3

Usage:
    python build_clean.py
"""
import csv
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from config import CITIES, CLEAN_DIR, CLEAN_FILE, RAW_DIR  # noqa: E402

FIELDNAMES = [
    "city", "country", "latitude", "longitude", "timestamp_utc", "aqi_owm",
    "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3",
]


def iter_raw_records():
    """Parcourt tous les fichiers raw/ et yield un dict normalisé par mesure horaire."""
    for fname in sorted(os.listdir(RAW_DIR)):
        if not fname.endswith(".json"):
            continue
        filepath = os.path.join(RAW_DIR, fname)
        with open(filepath, encoding="utf-8") as f:
            record = json.load(f)

        city = record["city"]
        if city not in CITIES:
            continue
        lat, lon, country = CITIES[city]
        api_list = record.get("raw_response", {}).get("list", [])

        for entry in api_list:
            dt_unix = entry.get("dt")
            if dt_unix is None:
                continue
            ts = datetime.fromtimestamp(dt_unix, tz=timezone.utc).isoformat()
            components = entry.get("components", {})
            main_aqi = entry.get("main", {}).get("aqi")

            yield {
                "city": city,
                "country": country,
                "latitude": lat,
                "longitude": lon,
                "timestamp_utc": ts,
                "aqi_owm": main_aqi,
                "co": components.get("co"),
                "no": components.get("no"),
                "no2": components.get("no2"),
                "o3": components.get("o3"),
                "so2": components.get("so2"),
                "pm2_5": components.get("pm2_5"),
                "pm10": components.get("pm10"),
                "nh3": components.get("nh3"),
            }


def main():
    seen = {}  # (city, timestamp_utc) -> record ; dernier vu gagne
    count_in = 0
    for rec in iter_raw_records():
        count_in += 1
        key = (rec["city"], rec["timestamp_utc"])
        seen[key] = rec

    rows = sorted(seen.values(), key=lambda r: (r["timestamp_utc"], r["city"]))

    os.makedirs(CLEAN_DIR, exist_ok=True)
    with open(CLEAN_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Lu {count_in} mesures brutes -> {len(rows)} lignes uniques dans {CLEAN_FILE}")


if __name__ == "__main__":
    main()
