"""
load_warehouse.py — Charge storage/clean/clean.csv dans le data warehouse Postgres.
Rejouable : upsert sur les dimensions, insert-si-absent sur la table de faits
(pas de doublons même si on relance sur les mêmes données).

Variables d'environnement attendues :
    DATABASE_URL=postgresql://user:password@host:port/dbname

Usage:
    python load_warehouse.py
"""
import csv
import os
import sys
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ingestion"))
from config import CLEAN_FILE  # noqa: E402

DAY_NAMES_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def get_connection():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERREUR: variable d'environnement DATABASE_URL manquante.", file=sys.stderr)
        sys.exit(1)
    return psycopg2.connect(dsn)


def apply_schema(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, encoding="utf-8") as f:
        ddl = f.read()
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()


def upsert_city(cur, city, country, lat, lon):
    cur.execute(
        """
        INSERT INTO dim_city (city_name, country, latitude, longitude)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (city_name, country) DO UPDATE
            SET latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude
        RETURNING city_key
        """,
        (city, country, lat, lon),
    )
    return cur.fetchone()[0]


def upsert_time(cur, ts_iso: str):
    ts = datetime.fromisoformat(ts_iso)
    dow = ts.weekday()  # 0=lundi
    cur.execute(
        """
        INSERT INTO dim_time (timestamp_utc, date, hour, day_of_week, day_name, is_weekend, month, year)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp_utc) DO UPDATE SET timestamp_utc = EXCLUDED.timestamp_utc
        RETURNING time_key
        """,
        (ts, ts.date(), ts.hour, dow, DAY_NAMES_FR[dow], dow >= 5, ts.month, ts.year),
    )
    return cur.fetchone()[0]


def main():
    conn = get_connection()
    apply_schema(conn)

    inserted, skipped = 0, 0
    with open(CLEAN_FILE, encoding="utf-8") as f, conn.cursor() as cur:
        reader = csv.DictReader(f)
        for row in reader:
            city_key = upsert_city(
                cur, row["city"], row["country"], row["latitude"], row["longitude"]
            )
            time_key = upsert_time(cur, row["timestamp_utc"])

            cur.execute(
                """
                INSERT INTO fact_air_quality
                    (city_key, time_key, aqi_owm, co, no, no2, o3, so2, pm2_5, pm10, nh3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (city_key, time_key) DO NOTHING
                """,
                (
                    city_key, time_key,
                    row["aqi_owm"] or None, row["co"] or None, row["no"] or None,
                    row["no2"] or None, row["o3"] or None, row["so2"] or None,
                    row["pm2_5"] or None, row["pm10"] or None, row["nh3"] or None,
                ),
            )
            if cur.rowcount:
                inserted += 1
            else:
                skipped += 1

    conn.commit()
    conn.close()
    print(f"Chargement terminé : {inserted} lignes insérées, {skipped} déjà présentes.")


if __name__ == "__main__":
    main()
