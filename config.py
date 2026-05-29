from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

DATA_DIR = ROOT_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PREDICTIONS_DIR = DATA_DIR / "predictions"
LIVE_DATA_DIR = DATA_DIR / "live"

MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = DATA_DIR / "logs"

for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    PREDICTIONS_DIR,
    LIVE_DATA_DIR,
    MODELS_DIR,
    LOGS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)


MASTER_DATASET_PATH = (
    PROCESSED_DATA_DIR /
    "master_energy_dataset.csv"
)

MERGED_DATASET = (
    PROCESSED_DATA_DIR /
    "merged_historic_demand.csv"
)

ENGINEERED_DATASET = (
    PROCESSED_DATA_DIR /
    "engineered_features.csv"
)

FEATURE_STORE_PATH = (
    PROCESSED_DATA_DIR /
    "feature_store.csv"
)

GRID_STRESS_DATASET_PATH = (
    PROCESSED_DATA_DIR /
    "grid_stress_dataset.csv"
)

GRID_STRESS_DATASET = (
    PROCESSED_DATA_DIR /
    "grid_stress_features.csv"
)

PRICING_DATASET_PATH = (
    PROCESSED_DATA_DIR /
    "pricing_model_dataset.csv"
)

PRICING_DATASET = PRICING_DATASET_PATH

CENTRALIZED_DATASET_PATH = (
    PROCESSED_DATA_DIR /
    "centralized_energy_dataset.csv"
)

CENTRALIZED_DATASET = CENTRALIZED_DATASET_PATH

FORECAST_DATASET_PATH = (
    PREDICTIONS_DIR /
    "future_7day_forecast.csv"
)

FORECAST_FILE = FORECAST_DATASET_PATH

OPTIMIZED_SCHEDULE_PATH = (
    PREDICTIONS_DIR /
    "optimized_schedules.csv"
)

OPTIMIZED_SCHEDULE_FILE = OPTIMIZED_SCHEDULE_PATH

RECOMMENDATION_PATH = (
    PREDICTIONS_DIR /
    "schedule_recommendations.csv"
)

RECOMMENDATION_FILE = RECOMMENDATION_PATH

LIVE_DATA_PATH = (
    LIVE_DATA_DIR /
    "live_grid_data.csv"
)


PATHS = {
    "pricing_dataset": PRICING_DATASET_PATH,
    "optimized_schedule": OPTIMIZED_SCHEDULE_PATH,
    "schedule_recommendations": RECOMMENDATION_PATH,
    "future_forecast": FORECAST_DATASET_PATH,
    "master_dataset": MASTER_DATASET_PATH,
    "centralized_dataset": CENTRALIZED_DATASET_PATH,
    "feature_store": FEATURE_STORE_PATH,
    "grid_stress_dataset": GRID_STRESS_DATASET_PATH,
    "live_data": LIVE_DATA_PATH,
}


RANDOM_SEED = 42
MODEL_RANDOM_STATE = RANDOM_SEED

FORECAST_HORIZON_DAYS = 7
FORECAST_HORIZON_HOURS = FORECAST_HORIZON_DAYS * 24
FORECAST_INTERVAL_MINUTES = 30
SETTLEMENT_PERIODS_PER_DAY = 48

TEST_SIZE = 0.2


TOP_K_RECOMMENDATIONS = 3
MAX_HOUSEHOLD_POWER_KW = 10

OPTIMIZATION_WEIGHTS = {
    "cost_weight": 0.40,
    "stress_weight": 0.25,
    "carbon_weight": 0.15,
    "renewable_weight": 0.10,
    "discomfort_weight": 0.10
}

NORMALIZATION_LIMITS = {
    "price_min": 0,
    "price_max": 200,
    "stress_min": 0,
    "stress_max": 1,
    "carbon_min": 0,
    "carbon_max": 500
}


USER_SETTINGS = {
    "top_k_recommendations": TOP_K_RECOMMENDATIONS,
    "default_region": "Midlands",
    "automatic_mode": True
}


GRID_STRESS_WEIGHTS = {
    "demand": 0.40,
    "transmission": 0.25,
    "renewables": 0.15,
    "interconnectors": 0.10,
    "storage": 0.05,
    "peak": 0.05
}


REGIONAL_SETTINGS = {
    "London": {
        "weight": 1.20,
        "demand_weight": 0.16,
        "price_multiplier": 1.18,
        "renewable_factor": 0.90,
        "congestion_factor": 1.15,
        "economic_factor": 1.20,
        "volatility": 0.06
    },

    "South_East": {
        "weight": 1.12,
        "demand_weight": 0.14,
        "price_multiplier": 1.12,
        "renewable_factor": 0.95,
        "congestion_factor": 1.10,
        "economic_factor": 1.10,
        "volatility": 0.05
    },

    "Midlands": {
        "weight": 1.00,
        "demand_weight": 0.13,
        "price_multiplier": 1.00,
        "renewable_factor": 1.00,
        "congestion_factor": 1.00,
        "economic_factor": 1.00,
        "volatility": 0.04
    },

    "North_West": {
        "weight": 0.96,
        "demand_weight": 0.11,
        "price_multiplier": 0.95,
        "renewable_factor": 1.05,
        "congestion_factor": 0.95,
        "economic_factor": 0.92,
        "volatility": 0.05
    },

    "Scotland": {
        "weight": 0.90,
        "demand_weight": 0.10,
        "price_multiplier": 0.88,
        "renewable_factor": 1.20,
        "congestion_factor": 0.85,
        "economic_factor": 0.85,
        "volatility": 0.07
    },

    "Wales": {
        "weight": 0.92,
        "demand_weight": 0.07,
        "price_multiplier": 0.92,
        "renewable_factor": 1.15,
        "congestion_factor": 0.90,
        "economic_factor": 0.90,
        "volatility": 0.05
    },

    "South_West": {
        "weight": 0.94,
        "demand_weight": 0.09,
        "price_multiplier": 0.96,
        "renewable_factor": 1.10,
        "congestion_factor": 0.92,
        "economic_factor": 0.94,
        "volatility": 0.05
    }
}

REGIONS = list(REGIONAL_SETTINGS.keys())


RETRAIN_DAY = 6
RETRAIN_ERROR_THRESHOLD = 8.0

APP_NAME = "GridFlex AI"
APP_VERSION = "2.0"
TIMEZONE = "Europe/London"


DEBUG_MODE = True