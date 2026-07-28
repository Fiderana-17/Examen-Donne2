# DONNEES2 — Pipeline AQI

## Villes couvertes
| Ville | Pays | Latitude | Longitude |
|---|---|---|---|
| Antananarivo | MG | -18.8792 | 47.5079 |
| New Delhi | IN | 28.6139 | 77.2090 |
| Beijing | CN | 39.9042 | 116.4074 |
| Paris | FR | 48.8566 | 2.3522 |
| Los Angeles | US | 34.0522 | -118.2437 |

*(Modifiez cette liste dans ingestion/config.py si le groupe change de villes.)*

## Colonnes de storage/clean/clean.csv
| Colonne | Unité / format |
|---|---|
| city | texte |
| country | code ISO pays |
| latitude, longitude | degrés décimaux |
| timestamp_utc | ISO 8601, UTC |
| aqi_owm | indice OWM 1 (bon) à 5 (très mauvais) — *pas* l'AQI US 0-500 |
| co, no, no2, o3, so2, pm2_5, pm10, nh3 | concentration en µg/m³ |

## Schéma du warehouse
Voir ARCHITECTURE.md et warehouse/schema.sql (schéma en étoile : fact_air_quality, dim_city, dim_time).

## Période couverte
Fin avril 2026 → 28 juillet 2026 (~3 mois de backfill), avec enrichissement horaire continu depuis via le pipeline automatique GitHub Actions. *10 433 mesures* chargées à date, réparties sur les 5 villes.

Trous connus : aucun trou significatif identifié sur la période de backfill ; l'alimentation horaire continue peut ponctuellement manquer une heure en cas d'échec de run (retries automatiques configurés dans le workflow).

## Connexion à la base
Host: ep-small-silence-asl5y809-pooler.c-4.eu-central-1.aws.neon.tech
Port: 5432
Database: (nom transmis séparément)
SSL: sslmode=require
(identifiants complets transmis séparément / stockés en secrets GitHub Actions,
jamais commit dans ce dépôt)

## Notebook d'exploration
Un notebook d'exploration des données (évolution de l'AQI par ville, comparaison weekend/semaine, corrélations entre polluants) est disponible dans notebooks/exploration_aqi.ipynb, réalisé sur Google Colab.

## Orchestrateur
Le pipeline tourne automatiquement toutes les heures via *GitHub Actions* (.github/workflows/aqi_pipeline.yml), enchaînant : collecte API → reconstruction de clean.csv → chargement du warehouse. Voir ARCHITECTURE.md pour la justification de ce choix par rapport à Airflow.

## Comment relancer le pipeline manuellement
pip install -r requirements.txt
cp .env.example .env   # puis remplir les vraies valeurs
export $(cat .env | xargs)   # PowerShell : voir instructions dans le rapport de projet

python ingestion/backfill.py --months 3
python ingestion/fetch_api.py
python transform/build_clean.py
python warehouse/load_warehouse.py