

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from config import (
    GRID_STRESS_DATASET_PATH,
    FORECAST_HORIZON_HOURS,
    FORECAST_INTERVAL_MINUTES,
    MODELS_DIR,
    PREDICTIONS_DIR,
    RANDOM_SEED,
)

from centralized_dataset_manager import (
    CENTRALIZED_OUTPUT_FILE,
)


MODEL_FILE = MODELS_DIR / "demand_forecasting_model.pkl"
INPUT_FILE = GRID_STRESS_DATASET_PATH

OUTPUT_FILE = PREDICTIONS_DIR / "future_7day_forecast.csv"


FEATURE_COLUMNS = [

    # Time
    "MONTH",
    "DAY",
    "DAY_OF_WEEK",
    "HOUR",
    "IS_WEEKEND",

    # Grid
    "TSD",
    "GRID_STRESS_SCORE",

    # Renewables
    "RENEWABLE_RATIO",
    "RENEWABLE_UTILIZATION",

    # Carbon
    "CARBON_INTENSITY_SCORE",

    # Interconnectors
    "TOTAL_INTERCONNECTOR_FLOW",

    # Lag features
    "ND_LAG_1",
    "ND_LAG_48",
    "ND_LAG_336",

    # Rolling
    "ND_ROLLING_6H",
    "ND_ROLLING_24H",
    "ND_ROLLING_7D",
]

TARGET_COLUMN = "ND"

def load_dataset():

    print("Loading grid stress dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Grid stress dataset not found:\n{INPUT_FILE}\n"
            "Run forecasting.grid_stress first."
        )

    df = pd.read_csv(INPUT_FILE)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], errors="coerce")
    df = df.sort_values("TIMESTAMP").reset_index(drop=True)

    return df


def validate_features(df):

    missing = [
        col
        for col in FEATURE_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing forecast features:\n{missing}"
        )

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Missing target column: {TARGET_COLUMN}"
        )


def split_dataset(df):

    split_index = int(len(df) * 0.90)

    train_df = df.iloc[:split_index].copy()

    test_df = df.iloc[split_index:].copy()

    return train_df, test_df


def train_forecasting_model(train_df):

    print("\nTraining demand forecasting model...")

    X_train = train_df[FEATURE_COLUMNS]

    y_train = train_df[TARGET_COLUMN]

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=18,
        min_samples_split=5,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    return model


def evaluate_model(model, test_df):

    print("\nEvaluating forecasting model...")

    X_test = test_df[FEATURE_COLUMNS]

    y_test = test_df[TARGET_COLUMN]

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)

    rmse = np.sqrt(
        mean_squared_error(y_test, predictions)
    )

    mape = np.mean(
        np.abs((y_test - predictions) / y_test)
    ) * 100

    print("\nForecast Performance")
    print(f"MAE: {round(mae, 2)} MW")
    print(f"RMSE: {round(rmse, 2)} MW")
    print(f"MAPE: {round(mape, 2)}%")


def save_model(model):

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print(f"\nModel saved:\n{MODEL_FILE}")


def load_existing_model():

    if MODEL_FILE.exists():

        print("\nLoading existing model...")

        return joblib.load(MODEL_FILE)

    return None


def create_future_timestamps(last_timestamp):

    forecast_periods = int(
        (FORECAST_HORIZON_HOURS * 60)
        / FORECAST_INTERVAL_MINUTES
    )

    timestamps = pd.date_range(
        start=(
            last_timestamp
            + pd.Timedelta(
                minutes=FORECAST_INTERVAL_MINUTES
            )
        ),
        periods=forecast_periods,
        freq=f"{FORECAST_INTERVAL_MINUTES}min"
    )

    return timestamps


def create_future_feature_frame(
    latest_row,
    future_timestamps
):

    rows = []

    current_nd = latest_row["ND"]

    for ts in future_timestamps:

        row = latest_row.copy()

        row["TIMESTAMP"] = ts
        row["MONTH"] = ts.month
        row["DAY"] = ts.day
        row["DAY_OF_WEEK"] = ts.dayofweek
        row["HOUR"] = ts.hour
        row["IS_WEEKEND"] = 1 if ts.dayofweek >= 5 else 0

        hour_factor = (
            1
            + (
                0.08
                * np.sin(
                    2 * np.pi * ts.hour / 24
                )
            )
        )

        current_nd = current_nd * hour_factor

        row["ND_LAG_1"] = current_nd
        row["ND_LAG_336"] = current_nd
        row["ND_LAG_48"] = current_nd

        row["ND_ROLLING_MEAN_6H"] = current_nd
        row["ND_ROLLING_MEAN_24H"] = current_nd
        row["ND_ROLLING_MEAN_7D"] = current_nd

        rows.append(row)

    future_df = pd.DataFrame(rows)

    return future_df


def generate_forecast(
    model,
    latest_row
):

    print("\nGenerating 7-day forecast...")

    future_timestamps = create_future_timestamps(
        latest_row["TIMESTAMP"]
    )

    future_df = create_future_feature_frame(
        latest_row,
        future_timestamps
    )

    X_future = future_df[FEATURE_COLUMNS]

    predictions = model.predict(X_future)

    future_df["PREDICTED_DEMAND"] = predictions

    return future_df


def save_forecast(forecast_df):

    PREDICTIONS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    forecast_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"\nForecast saved:\n{OUTPUT_FILE}")


def display_forecast_summary(df):

   
    print("GRIDFLEX AI FORECAST SUMMARY")
    

    print("\nForecast Start:")
    print(df["TIMESTAMP"].min())

    print("\nForecast End:")
    print(df["TIMESTAMP"].max())

    print("\nForecast Rows:")
    print(len(df))

    print("\nAverage Demand:")
    print(round(df["PREDICTED_DEMAND"].mean(), 2), "MW")

    print("\nPeak Demand:")
    print(round(df["PREDICTED_DEMAND"].max(), 2), "MW")


def run_future_forecast_pipeline():

    df = load_dataset()

    validate_features(df)

    train_df, test_df = split_dataset(df)

    model = load_existing_model()

    if model is None:

        model = train_forecasting_model(train_df)

        save_model(model)

    evaluate_model(model, test_df)

    latest_row = df.iloc[-1]

    forecast_df = generate_forecast(
        model,
        latest_row
    )

    save_forecast(forecast_df)

    display_forecast_summary(forecast_df)

    return forecast_df


if __name__ == "__main__":

    run_future_forecast_pipeline()

    print("\nForecasting complete.")