# =========================================================
# FILE: forecasting/forecast_model.py
# =========================================================

"""
GRIDFLEX AI — FORECAST MODEL
---------------------------------------------------------

Purpose
-------
Trains the core electricity demand forecasting model.

This script predicts:

- National Demand (ND)

Using:
--------
- Historical demand
- Weather-like cyclic patterns
- Renewable generation
- Calendar effects
- Rolling demand behaviour

This model feeds:
-----------------
1. Future demand forecasting
2. Grid stress prediction
3. Regional modelling
4. Optimization scheduling

Academic Importance
-------------------
This script forms the predictive intelligence layer
of the entire system.

The forecasting model is intentionally separated from:

- pricing
- market economics
- optimization

This improves:
---------------
- modularity
- realism
- dissertation rigor
- maintainability

Outputs
-------
models/demand_forecast_model.pkl
data/predictions/model_predictions.csv

"""

# =========================================================
# IMPORTS
# =========================================================

import joblib
import warnings

import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split

from config import (
    MODELS_DIR,
    PREDICTIONS_DIR,
    RANDOM_SEED
)

warnings.filterwarnings("ignore")

# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = (
    Path("data/processed/")
    / "grid_stress_dataset.csv"
)

MODEL_OUTPUT = (
    MODELS_DIR
    / "demand_forecast_model.pkl"
)

PREDICTIONS_OUTPUT = (
    PREDICTIONS_DIR
    / "model_predictions.csv"
)

TARGET_COLUMN = "ND"

# =========================================================
# FEATURE COLUMNS
# =========================================================

FEATURE_COLUMNS = [

    # Time Features
    "HOUR",
    "DAY_OF_WEEK",
    "MONTH",
    "IS_WEEKEND",

    # Lag Features
    "ND_LAG_1",
    "ND_LAG_48",

    # Rolling Features
    "ND_ROLLING_6H",
    "ND_ROLLING_7D",
    "ND_ROLLING_24H",

    # Renewable Features
    "TOTAL_RENEWABLE_GENERATION",
    "RENEWABLE_RATIO",

    # Grid Features
    "GRID_STRESS_SCORE",
    "PEAK_LOAD_INDICATOR",

    # Cyclical Features
    "HOUR_SIN",
    "HOUR_COS"

]

# =========================================================
# LOAD DATA
# =========================================================

def load_dataset():

    print("\nLoading forecast training dataset...")

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    if TARGET_COLUMN not in df.columns:

        raise ValueError(
            f"Missing target column: {TARGET_COLUMN}"
        )

    missing_features = [

        col for col in FEATURE_COLUMNS
        if col not in df.columns

    ]

    if missing_features:

        raise ValueError(
            f"Missing feature columns:\n"
            f"{missing_features}"
        )

    return df

# =========================================================
# PREPARE DATA
# =========================================================

def prepare_training_data(df):

    print("Preparing training data...")

    X = df[FEATURE_COLUMNS].copy()

    y = df[TARGET_COLUMN].copy()

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.ffill().bfill()

    return train_test_split(

        X,
        y,

        test_size=0.2,

        shuffle=False,

        random_state=RANDOM_SEED

    )

# =========================================================
# BUILD MODEL
# =========================================================

def build_model():

    print("Building Random Forest model...")

    model = RandomForestRegressor(

        n_estimators=200,

        max_depth=14,

        min_samples_split=5,

        min_samples_leaf=2,

        random_state=RANDOM_SEED,

        n_jobs=-1

    )

    return model

# =========================================================
# TRAIN MODEL
# =========================================================

def train_model(

    model,
    X_train,
    y_train

):

    print("Training forecast model...")

    model.fit(
        X_train,
        y_train
    )

    return model

# =========================================================
# EVALUATE MODEL
# =========================================================

def evaluate_model(

    model,
    X_test,
    y_test

):

    print("Evaluating model...")

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(

        mean_squared_error(
            y_test,
            predictions
        )

    )

    r2 = r2_score(
        y_test,
        predictions
    )

    metrics = {

        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2_SCORE": round(r2, 4)

    }

    print("\n===================================")
    print("MODEL PERFORMANCE")
    print("===================================")

    for key, value in metrics.items():

        print(f"{key}: {value}")

    return predictions, metrics

# =========================================================
# FEATURE IMPORTANCE
# =========================================================

def display_feature_importance(

    model

):

    print("\n===================================")
    print("FEATURE IMPORTANCE")
    print("===================================")

    importance_df = pd.DataFrame({

        "feature": FEATURE_COLUMNS,

        "importance": model.feature_importances_

    })

    importance_df = (

        importance_df
        .sort_values(
            "importance",
            ascending=False
        )

    )

    for row in importance_df.itertuples():

        print(
            f"{row.feature:<30}"
            f"{row.importance:.4f}"
        )

# =========================================================
# SAVE MODEL
# =========================================================

def save_model(model):

    MODEL_OUTPUT.parent.mkdir(

        parents=True,
        exist_ok=True

    )

    joblib.dump(
        model,
        MODEL_OUTPUT
    )

    print(
        f"\nModel saved:\n{MODEL_OUTPUT}"
    )

# =========================================================
# SAVE PREDICTIONS
# =========================================================

def save_predictions(

    df,
    predictions,
    y_test

):

    prediction_df = pd.DataFrame({

        "ACTUAL_ND": y_test.values,
        "PREDICTED_ND": predictions

    })

    PREDICTIONS_OUTPUT.parent.mkdir(

        parents=True,
        exist_ok=True

    )

    prediction_df.to_csv(

        PREDICTIONS_OUTPUT,
        index=False

    )

    print(
        f"\nPredictions saved:\n"
        f"{PREDICTIONS_OUTPUT}"
    )

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_forecast_training_pipeline():

    print("\n===================================")
    print("GRIDFLEX AI FORECAST MODEL")
    print("===================================")

    # Load
    df = load_dataset()

    # Split
    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = prepare_training_data(df)

    # Build
    model = build_model()

    # Train
    model = train_model(

        model,
        X_train,
        y_train

    )

    # Evaluate
    predictions, metrics = evaluate_model(

        model,
        X_test,
        y_test

    )

    # Importance
    display_feature_importance(
        model
    )

    # Save
    save_model(model)

    save_predictions(

        df,
        predictions,
        y_test

    )

    print("\nForecast model pipeline complete.")

    return model, metrics

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_forecast_training_pipeline()