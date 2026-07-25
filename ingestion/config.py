import os

API_KEY = os.environ.get("OWM_API_KEY")
CURRENT_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
HISTORY_URL = "http://api.openweathermap.org/data/2.5/air_pollution/history"

CITIES = {
    "Antananarivo": (-18.8792, 47.5079, "MG"),
    "New Delhi":    (28.6139, 77.2090, "IN"),
    "Beijing":      (39.9042, 116.4074, "CN"),
    "Paris":        (48.8566, 2.3522, "FR"),
    "Los Angeles":  (34.0522, -118.2437, "US"),
}

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "raw")
CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "clean")
CLEAN_FILE = os.path.join(CLEAN_DIR, "clean.csv")
