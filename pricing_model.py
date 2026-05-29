# =========================================================
# FILE: forecasting/grid_stress.py
# =========================================================

"""
GRID STRESS ENGINE
---------------------------------------------------------

Purpose:
--------
Calculates physical grid stress independently from pricing.

This script is VERY IMPORTANT academically because it
creates separation between:

1. Grid State
   - Physical infrastructure condition
   - Network pressure
   - Renewable support
   - Demand pressure

2. Market State
   - Electricity pricing
   - Tariffs
   - Market volatility
   - Supplier economics

This improves dissertation rigor because your optimization
is now balancing TWO independent objectives.

Produces:
---------
GRID_STRESS_SCORE
GRID_STATE
PEAK_RISK
RENEWABLE_RATIO

Output:
-------
data/processed/grid_stress_dataset.csv
"""

# =========================================================
# IMPORTS
# =========================================================

import numpy as np
import pandas as pd

from pathlib import Path

from config import (
    PROCESSED_DATA_DIR,
    RANDOM_SEED
)

# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = (
    PROCESSED_DATA_DIR /
    "feature_store.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR /
    "grid_stress_dataset.csv"
)

np.random.seed(RANDOM_SEED)

# =========================================================
# REQUIRED COLUMNS
# =========================================================

REQUIRED_COLUMNS = [

    "TIMESTAMP",
    "ND",

    "EMBEDDED_WIND_GENERATION",
    "EMBEDDED_SOLAR_GENERATION",

    "EMBEDDED_WIND_CAPACITY",
    "EMBEDDED_SOLAR_CAPACITY"

]

# =========================================================
# LOAD DATA
# =========================================================

def load_dataset():

    print("\nLoading feature engineered dataset...")

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Missing dataset:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    missing = [

        col for col in REQUIRED_COLUMNS
        if col not in df.columns

    ]

    if missing:

        raise ValueError(
            f"Missing required columns:\n{missing}"
        )

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"]
    )

    return df

# =========================================================
# SAFE NORMALIZATION
# =========================================================

def normalize(series):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:

        return pd.Series(
            np.zeros(len(series)),
            index=series.index
        )

    return (
        (series - minimum)
        /
        (maximum - minimum)
    )

# =========================================================
# RENEWABLE RATIO
# =========================================================

def calculate_renewable_ratio(df):

    print("Calculating renewable ratio...")

    renewable_generation = (

        df["EMBEDDED_WIND_GENERATION"]

        +

        df["EMBEDDED_SOLAR_GENERATION"]

    )

    renewable_capacity = (

        df["EMBEDDED_WIND_CAPACITY"]

        +

        df["EMBEDDED_SOLAR_CAPACITY"]

        +

        1
    )

    renewable_ratio = (

        renewable_generation
        /
        renewable_capacity

    )

    renewable_ratio = renewable_ratio.clip(
        lower=0,
        upper=1
    )

    df["RENEWABLE_RATIO"] = renewable_ratio

    return df

# =========================================================
# DEMAND PRESSURE
# =========================================================

def calculate_demand_pressure(df):

    print("Calculating demand pressure...")

    df["DEMAND_PRESSURE"] = normalize(
        df["ND"]
    )

    return df

# =========================================================
# PEAK LOAD INDICATOR
# =========================================================

def calculate_peak_indicator(df):

    print("Calculating peak load indicator...")

    df["HOUR"] = (
        df["TIMESTAMP"]
        .dt.hour
    )

    peak_hours = [

        7, 8, 9,
        17, 18, 19

    ]

    df["PEAK_LOAD_INDICATOR"] = np.where(

        df["HOUR"].isin(peak_hours),

        1,

        0

    )

    return df

# =========================================================
# GRID STRESS SCORE
# =========================================================

def calculate_grid_stress(df):

    print("Calculating grid stress score...")

    demand_component = (
        df["DEMAND_PRESSURE"]
        * 0.55
    )

    peak_component = (
        df["PEAK_LOAD_INDICATOR"]
        * 0.20
    )

    renewable_relief = (
        (1 - df["RENEWABLE_RATIO"])
        * 0.25
    )

    random_variation = np.random.normal(

        loc=0,
        scale=0.015,
        size=len(df)

    )

    stress_score = (

        demand_component

        +

        peak_component

        +

        renewable_relief

        +

        random_variation

    )

    stress_score = np.clip(
        stress_score,
        0,
        1
    )

    df["GRID_STRESS_SCORE"] = stress_score

    return df

# =========================================================
# GRID STATE CLASSIFICATION
# =========================================================

def classify_grid_state(df):

    print("Classifying grid states...")

    conditions = [

        df["GRID_STRESS_SCORE"] < 0.30,

        (
            (df["GRID_STRESS_SCORE"] >= 0.30)
            &
            (df["GRID_STRESS_SCORE"] < 0.60)
        ),

        (
            (df["GRID_STRESS_SCORE"] >= 0.60)
            &
            (df["GRID_STRESS_SCORE"] < 0.80)
        ),

        df["GRID_STRESS_SCORE"] >= 0.80

    ]

    labels = [

        "LOW",
        "MODERATE",
        "HIGH",
        "CRITICAL"

    ]

    df["GRID_STATE"] = np.select(
        conditions,
        labels,
        default="UNKNOWN"
    )

    return df

# =========================================================
# PEAK RISK
# =========================================================

def calculate_peak_risk(df):

    print("Calculating peak risk...")

    peak_risk = (

        (
            df["GRID_STRESS_SCORE"]
            * 0.7
        )

        +

        (
            df["PEAK_LOAD_INDICATOR"]
            * 0.3
        )

    )

    peak_risk = np.clip(
        peak_risk,
        0,
        1
    )

    df["PEAK_RISK"] = peak_risk

    return df

# =========================================================
# SUMMARY
# =========================================================

def display_summary(df):

    print("\n===================================")
    print("GRID STRESS SUMMARY")
    print("===================================")

    print(
        f"\nRows: {len(df):,}"
    )

    print(
        f"Average Stress: "
        f"{df['GRID_STRESS_SCORE'].mean():.3f}"
    )

    print(
        f"Max Stress: "
        f"{df['GRID_STRESS_SCORE'].max():.3f}"
    )

    print(
        f"Average Renewable Ratio: "
        f"{df['RENEWABLE_RATIO'].mean():.3f}"
    )

    print("\nGrid State Distribution:")

    print(
        df["GRID_STATE"]
        .value_counts()
    )

# =========================================================
# SAVE DATASET
# =========================================================

def save_dataset(df):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved:\n{OUTPUT_FILE}"
    )

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_grid_stress_pipeline():

    print("\n===================================")
    print("GRID STRESS ENGINE")
    print("===================================")

    df = load_dataset()

    df = calculate_renewable_ratio(df)

    df = calculate_demand_pressure(df)

    df = calculate_peak_indicator(df)

    df = calculate_grid_stress(df)

    df = classify_grid_state(df)

    df = calculate_peak_risk(df)

    display_summary(df)

    save_dataset(df)

    return df

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_grid_stress_pipeline()