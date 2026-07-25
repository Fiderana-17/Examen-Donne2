-- Schéma en étoile pour le data warehouse AQI
-- Règles respectées : pas de mesures dans les dimensions,
-- pas de colonnes descriptives dans la table de faits.

CREATE TABLE IF NOT EXISTS dim_city (
    city_key      SERIAL PRIMARY KEY,
    city_name     VARCHAR(100) NOT NULL,
    country       VARCHAR(10)  NOT NULL,
    latitude      DOUBLE PRECISION NOT NULL,
    longitude     DOUBLE PRECISION NOT NULL,
    UNIQUE (city_name, country)
);

CREATE TABLE IF NOT EXISTS dim_time (
    time_key      SERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMPTZ NOT NULL UNIQUE,
    date          DATE NOT NULL,
    hour          SMALLINT NOT NULL,
    day_of_week   SMALLINT NOT NULL,   -- 0=lundi ... 6=dimanche
    day_name      VARCHAR(10) NOT NULL,
    is_weekend    BOOLEAN NOT NULL,
    month         SMALLINT NOT NULL,
    year          SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_air_quality (
    fact_key      BIGSERIAL PRIMARY KEY,
    city_key      INTEGER NOT NULL REFERENCES dim_city(city_key),
    time_key      INTEGER NOT NULL REFERENCES dim_time(time_key),
    aqi_owm       SMALLINT,
    co            DOUBLE PRECISION,
    no            DOUBLE PRECISION,
    no2           DOUBLE PRECISION,
    o3            DOUBLE PRECISION,
    so2           DOUBLE PRECISION,
    pm2_5         DOUBLE PRECISION,
    pm10          DOUBLE PRECISION,
    nh3           DOUBLE PRECISION,
    UNIQUE (city_key, time_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_city ON fact_air_quality(city_key);
CREATE INDEX IF NOT EXISTS idx_fact_time ON fact_air_quality(time_key);
