# DONNEES2 — Pipeline AQI

## Villes couvertes
| Ville | Pays | Latitude | Longitude |
|---|---|---|---|
| Antananarivo | MG | -18.8792 | 47.5079 |
| New Delhi | IN | 28.6139 | 77.2090 |
| Beijing | CN | 39.9042 | 116.4074 |
| Paris | FR | 48.8566 | 2.3522 |
| Los Angeles | US | 34.0522 | -118.2437 |

*(Modifiez cette liste dans `ingestion/config.py` si le groupe change de villes.)*

## Colonnes de `storage/clean/clean.csv`
| Colonne | Unité / format |
|---|---|
| city | texte |
| country | code ISO pays |
| latitude, longitude | degrés décimaux |
| timestamp_utc | ISO 8601, UTC |
| aqi_owm | indice OWM 1 (bon) à 5 (très mauvais) — **pas** l'AQI US 0-500 |
| co, no, no2, o3, so2, pm2_5, pm10, nh3 | concentration en µg/m³ |

## Schéma du warehouse
Voir `ARCHITECTURE.md` et `warehouse/schema.sql` (schéma en étoile : `fact_air_quality`, `dim_city`, `dim_time`).

## Période couverte
[à compléter après le backfill : ex. "01/07/2025 → 17/07/2026, quelques trous en [dates] dus à [raison]"]

## Connexion à la base
```
Host: [à compléter]
Port: 5432
Database: [à compléter]
(identifiants transmis séparément / dans les secrets du dépôt)
```

## Comment relancer le pipeline manuellement
```bash
pip install -r requirements.txt
cp .env.example .env   # puis remplir les vraies valeurs
export $(cat .env | xargs)

python ingestion/backfill.py --months 3
python ingestion/fetch_api.py
python transform/build_clean.py
python warehouse/load_warehouse.py
```
