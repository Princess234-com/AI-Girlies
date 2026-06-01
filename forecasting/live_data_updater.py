# =========================================================
# FILE: forecasting/live_data_updater.py
# =========================================================

"""
GRIDFLEX AI — LIVE DATA UPDATER
---------------------------------------------------------

Purpose
-------
Simulates a live smart-grid data ingestion system.

This script:

1. Loads latest processed dataset
2. Simulates incoming live measurements
3. Updates:
   - demand
   - renewables
   - grid stress
   - pricing
4. Saves rolling live dataset

Academic Importance
-------------------
This transforms your project from:

STATIC FORECASTING
→
ADAPTIVE ENERGY INTELLIGENCE

This is extremely valuable academically because it shows:

- streaming architecture
- continual updating
- near real-time intelligence
- smart-grid realism

IMPORTANT
---------
This is NOT true real-time ingestion.

It is a realistic simulation layer suitable for:
- dissertations
- demos
- prototypes
- architecture validation

Outputs
-------
data/live/live_grid_data.csv

"""

# =========================================================
# IMPORTS
# =========================================================

import numpy as np
import pandas as pd

from datetime import timedelta
from pathlib import Path

from config import (
    LIVE_DATA_DIR,
    RANDOM_SEED
)

# =========================================================
# CONFIG
# =========================================================

np.random.seed(RANDOM_SEED)

INPUT_FILE = (
    Path("data/processed/")
    / "pricing_model_dataset.csv"
)

OUTPUT_FILE = (
    LIVE_DATA_DIR
    / "live_grid_data.csv"
)

MAX_ROWS = 5000

# =========================================================
# LOAD BASE DATASET
# =========================================================

def load_base_dataset():

    print("\nLoading base dataset...")

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"]
    )

    return df

# =========================================================
# GENERATE LIVE RECORD
# =========================================================

def generate_live_record(last_row):

    # =====================================================
    # NEXT TIMESTAMP
    # =====================================================

    next_timestamp = (

        pd.to_datetime(
            last_row["TIMESTAMP"]
        )

        +

        timedelta(minutes=30)

    )

    # =====================================================
    # DEMAND SIMULATION
    # =====================================================

    demand_noise = np.random.normal(
        loc=0,
        scale=450
    )

    next_demand = (

        last_row["ND"]

        +

        demand_noise

    )

    next_demand = max(
        next_demand,
        10000
    )

    # =====================================================
    # RENEWABLE GENERATION
    # =====================================================

    renewable_noise = np.random.normal(
        loc=0,
        scale=120
    )

    wind_generation = max(

        last_row[
            "EMBEDDED_WIND_GENERATION"
        ]

        +

        renewable_noise,

        0

    )

    solar_generation = max(

        last_row[
            "EMBEDDED_SOLAR_GENERATION"
        ]

        +

        renewable_noise * 0.5,

        0

    )

    # =====================================================
    # RENEWABLE RATIO
    # =====================================================

    renewable_capacity = (

        last_row[
            "EMBEDDED_WIND_CAPACITY"
        ]

        +

        last_row[
            "EMBEDDED_SOLAR_CAPACITY"
        ]

        +

        1

    )

    renewable_ratio = (

        wind_generation
        +
        solar_generation

    ) / renewable_capacity

    renewable_ratio = np.clip(
        renewable_ratio,
        0,
        1
    )

    # =====================================================
    # GRID STRESS
    # =====================================================

    demand_pressure = (
        next_demand / 50000
    )

    grid_stress = (

        demand_pressure * 0.7

        +

        (1 - renewable_ratio) * 0.3

    )

    grid_stress = np.clip(
        grid_stress,
        0,
        1
    )

    # =====================================================
    # PRICE SIMULATION
    # =====================================================

    market_noise = np.random.normal(
        loc=0,
        scale=3
    )

    national_price = (

        50

        +

        grid_stress * 70

        +

        market_noise

    )

    national_price = max(
        national_price,
        20
    )

    # =====================================================
    # MARKET STATE
    # =====================================================

    if national_price < 60:

        market_state = "LOW"

    elif national_price < 90:

        market_state = "NORMAL"

    elif national_price < 120:

        market_state = "HIGH"

    else:

        market_state = "CRITICAL"

    # =====================================================
    # RETURN RECORD
    # =====================================================

    return {

        "TIMESTAMP":
        next_timestamp,

        "ND":
        round(next_demand, 2),

        "EMBEDDED_WIND_GENERATION":
        round(wind_generation, 2),

        "EMBEDDED_SOLAR_GENERATION":
        round(solar_generation, 2),

        "EMBEDDED_WIND_CAPACITY":
        last_row[
            "EMBEDDED_WIND_CAPACITY"
        ],

        "EMBEDDED_SOLAR_CAPACITY":
        last_row[
            "EMBEDDED_SOLAR_CAPACITY"
        ],

        "RENEWABLE_RATIO":
        round(renewable_ratio, 4),

        "GRID_STRESS_SCORE":
        round(grid_stress, 4),

        "NATIONAL_PRICE":
        round(national_price, 2),

        "MARKET_STATE":
        market_state

    }

# =========================================================
# APPEND LIVE DATA
# =========================================================

def append_live_data(

    df,
    iterations=48

):

    print(
        f"\nGenerating "
        f"{iterations} live records..."
    )

    records = []

    last_row = df.iloc[-1]

    for _ in range(iterations):

        new_record = generate_live_record(
            last_row
        )

        records.append(new_record)

        last_row = new_record

    live_df = pd.DataFrame(records)

    updated_df = pd.concat(

        [
            df,
            live_df
        ],

        ignore_index=True

    )

    # =====================================================
    # ROLLING DATASET
    # =====================================================

    updated_df = updated_df.tail(
        MAX_ROWS
    )

    return updated_df

# =========================================================
# DISPLAY SUMMARY
# =========================================================

def display_summary(df):

    print("\n===================================")
    print("LIVE DATA SUMMARY")
    print("===================================")

    print(
        f"\nRows: {len(df):,}"
    )

    latest = df.iloc[-1]

    print(
        f"\nLatest Timestamp: "
        f"{latest['TIMESTAMP']}"
    )

    print(
        f"Latest Demand: "
        f"{latest['ND']:.2f} MW"
    )

    print(
        f"Latest Grid Stress: "
        f"{latest['GRID_STRESS_SCORE']:.3f}"
    )

    print(
        f"Latest Price: £"
        f"{latest['NATIONAL_PRICE']:.2f}"
    )

    print(
        f"Market State: "
        f"{latest['MARKET_STATE']}"
    )

# =========================================================
# SAVE LIVE DATA
# =========================================================

def save_live_dataset(df):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved live dataset:\n"
        f"{OUTPUT_FILE}"
    )

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_live_data_pipeline():

    print("\n===================================")
    print("GRIDFLEX AI LIVE DATA ENGINE")
    print("===================================")

    # Load
    df = load_base_dataset()

    # Generate updates
    updated_df = append_live_data(
        df,
        iterations=48
    )

    # Summary
    display_summary(updated_df)

    # Save
    save_live_dataset(updated_df)

    print(
        "\nLive data update complete."
    )

    return updated_df

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_live_data_pipeline()