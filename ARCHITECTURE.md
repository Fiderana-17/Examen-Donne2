# Architecture

> À compléter/adapter par le groupe — remplacez les [placeholders] et justifiez chaque choix en une phrase.

| Composant | Choix | Justification |
|---|---|---|
| API AQI | OpenWeatherMap Air Pollution API | [à justifier : gratuite, historique dispo, couverture globale des 5 villes] |
| Orchestrateur | Apache Airflow (Docker) | [à justifier : déjà en place pour le cours data engineering, DAGs versionnables] |
| Stockage raw/clean | Fichiers locaux / [bucket ?] | [à justifier] |
| Data Warehouse | PostgreSQL (Neon) | [à justifier : gratuit, accès distant vérifiable, déjà utilisé sur d'autres projets] |
| Modélisation | Schéma en étoile | [à justifier : granularité simple ville x heure, pas besoin de flocon] |

## Schéma du warehouse

```
dim_city ──┐
           ├──> fact_air_quality
dim_time ──┘
```

- **fact_air_quality** : aqi_owm, co, no, no2, o3, so2, pm2_5, pm10, nh3 + clés vers dim_city et dim_time
- **dim_city** : city_name, country, latitude, longitude
- **dim_time** : date, hour, day_of_week, day_name, is_weekend, month, year
