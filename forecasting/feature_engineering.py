# =========================================================
# GRIDFLEX AI — FEATURE ENGINEERING PIPELINE
# forecasting/feature_engineering.py
# =========================================================

import numpy as np
import pandas as pd

from pathlib import Path

from config import (
    PROCESSED_DATA_DIR,
    RANDOM_SEED
)

# =========================================================
# FILE PATHS
# =========================================================

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "master_energy_dataset.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "feature_store.csv"
)

# =========================================================
# RANDOM SEED
# =========================================================

np.random.seed(RANDOM_SEED)

# =========================================================
# REQUIRED COLUMNS
# =========================================================

REQUIRED_COLUMNS = [

    "TIMESTAMP",

    "ND",

    "TSD",

    "EMBEDDED_WIND_GENERATION",
    "EMBEDDED_SOLAR_GENERATION",

    "EMBEDDED_WIND_CAPACITY",
    "EMBEDDED_SOLAR_CAPACITY",

    "IFA_FLOW",
    "IFA2_FLOW",
    "BRITNED_FLOW",

    "MOYLE_FLOW",
    "EAST_WEST_FLOW",

    "NEMO_FLOW",
    "NSL_FLOW",

    "ELECLINK_FLOW",
    "VIKING_FLOW",

    "GREENLINK_FLOW",

    "NON_BM_STOR",

    "SCOTTISH_TRANSFER"

]

# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    print("\nLoading master dataset...")

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Missing file:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    # =====================================================
    # TIMESTAMP
    # =====================================================

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"]
    )

    # =====================================================
    # SORT
    # =====================================================

    df = df.sort_values(
        "TIMESTAMP"
    ).reset_index(drop=True)

    # =====================================================
    # VALIDATION
    # =====================================================

    missing = [

        col for col in REQUIRED_COLUMNS

        if col not in df.columns

    ]

    if len(missing) > 0:

        raise ValueError(
            f"Missing required columns:\n{missing}"
        )

    print(
        f"Loaded dataset shape: {df.shape}"
    )

    return df


# =========================================================
# TIME FEATURES
# =========================================================

def create_time_features(df):

    print("\nCreating time features...")

    # =====================================================
    # BASIC TIME
    # =====================================================

    df["HOUR"] = (
        df["TIMESTAMP"].dt.hour
    )

    df["DAY_OF_WEEK"] = (
        df["TIMESTAMP"].dt.dayofweek
    )

    df["MONTH"] = (
        df["TIMESTAMP"].dt.month
    )

    df["DAY_OF_YEAR"] = (
        df["TIMESTAMP"].dt.dayofyear
    )

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"] >= 5
    ).astype(int)

    # =====================================================
    # CYCLICAL ENCODING
    # =====================================================

    df["HOUR_SIN"] = np.sin(
        2 * np.pi * df["HOUR"] / 24
    )

    df["HOUR_COS"] = np.cos(
        2 * np.pi * df["HOUR"] / 24
    )

    df["MONTH_SIN"] = np.sin(
        2 * np.pi * df["MONTH"] / 12
    )

    df["MONTH_COS"] = np.cos(
        2 * np.pi * df["MONTH"] / 12
    )

    return df


# =========================================================
# DEMAND FEATURES
# =========================================================

def create_demand_features(df):

    print("\nCreating demand features...")

    # =====================================================
    # LAG FEATURES
    # =====================================================

    df["ND_LAG_1"] = df["ND"].shift(1)

    df["ND_LAG_48"] = df["ND"].shift(48)

    df["ND_LAG_336"] = df["ND"].shift(336)

    # =====================================================
    # ROLLING AVERAGES
    # =====================================================

    df["ND_ROLLING_6H"] = (
        df["ND"]
        .rolling(12)
        .mean()
    )

    df["ND_ROLLING_24H"] = (
        df["ND"]
        .rolling(48)
        .mean()
    )

    df["ND_ROLLING_7D"] = (
        df["ND"]
        .rolling(336)
        .mean()
    )

    # =====================================================
    # PEAK INDICATOR
    # =====================================================

    demand_threshold = (
        df["ND"].quantile(0.90)
    )

    df["IS_PEAK_DEMAND"] = (

        df["ND"]
        >=
        demand_threshold

    ).astype(int)

    return df


# =========================================================
# RENEWABLE FEATURES
# =========================================================

def create_renewable_features(df):

    print("\nCreating renewable features...")

    # =====================================================
    # TOTAL RENEWABLE GENERATION
    # =====================================================

    df["TOTAL_RENEWABLE_GENERATION"] = (

        df["EMBEDDED_WIND_GENERATION"]

        +

        df["EMBEDDED_SOLAR_GENERATION"]

    )

    # =====================================================
    # TOTAL RENEWABLE CAPACITY
    # =====================================================

    df["TOTAL_RENEWABLE_CAPACITY"] = (

        df["EMBEDDED_WIND_CAPACITY"]

        +

        df["EMBEDDED_SOLAR_CAPACITY"]

    )

    # =====================================================
    # RENEWABLE UTILIZATION
    # =====================================================

    df["RENEWABLE_UTILIZATION"] = (

        df["TOTAL_RENEWABLE_GENERATION"]

        /

        (
            df["TOTAL_RENEWABLE_CAPACITY"]
            + 1
        )

    )

    # =====================================================
    # RENEWABLE RATIO
    # =====================================================

    df["RENEWABLE_RATIO"] = (

        df["TOTAL_RENEWABLE_GENERATION"]

        /

        (
            df["ND"] + 1
        )

    )

    return df


# =========================================================
# INTERCONNECTOR FEATURES
# =========================================================

def create_interconnector_features(df):

    print("\nCreating interconnector features...")

    interconnector_cols = [

        "IFA_FLOW",
        "IFA2_FLOW",
        "BRITNED_FLOW",

        "MOYLE_FLOW",
        "EAST_WEST_FLOW",

        "NEMO_FLOW",
        "NSL_FLOW",

        "ELECLINK_FLOW",
        "VIKING_FLOW",

        "GREENLINK_FLOW"

    ]

    # =====================================================
    # TOTAL IMPORT / EXPORT
    # =====================================================

    df["TOTAL_INTERCONNECTOR_FLOW"] = (
        df[interconnector_cols]
        .sum(axis=1)
    )

    # =====================================================
    # ABSOLUTE FLOW
    # =====================================================

    df["ABS_INTERCONNECTOR_FLOW"] = (
        df[interconnector_cols]
        .abs()
        .sum(axis=1)
    )

    # =====================================================
    # IMPORT DEPENDENCY
    # =====================================================

    df["INTERCONNECTOR_DEPENDENCY"] = (

        df["ABS_INTERCONNECTOR_FLOW"]

        /

        (
            df["ND"] + 1
        )

    )

    return df


# =========================================================
# STORAGE FEATURES
# =========================================================

def create_storage_features(df):

    print("\nCreating storage features...")

    df["STORAGE_RATIO"] = (

        df["NON_BM_STOR"]

        /

        (
            df["ND"] + 1
        )

    )

    return df


# =========================================================
# GRID TRANSFER FEATURES
# =========================================================

def create_transfer_features(df):

    print("\nCreating transfer features...")

    df["SCOTLAND_TRANSFER_RATIO"] = (

        df["SCOTTISH_TRANSFER"]

        /

        (
            df["ND"] + 1
        )

    )

    return df


# =========================================================
# MARKET FEATURES
# =========================================================

def create_market_features(df):

    print("\nCreating market features...")

    # =====================================================
    # PEAK PRICING WINDOW
    # =====================================================

    df["IS_PEAK_PRICING_PERIOD"] = (

        (
            df["HOUR"] >= 16
        )

        &

        (
            df["HOUR"] <= 20
        )

    ).astype(int)

    # =====================================================
    # OFF PEAK
    # =====================================================

    df["IS_OFF_PEAK"] = (

        (
            df["HOUR"] >= 0
        )

        &

        (
            df["HOUR"] <= 5
        )

    ).astype(int)

    return df


# =========================================================
# CARBON INTENSITY PROXY
# =========================================================

def create_carbon_features(df):

    print("\nCreating carbon features...")

    renewable_component = (
        1 - df["RENEWABLE_RATIO"]
    )

    gas_proxy = (
        df["ND"] / (
            df["ND"].max() + 1
        )
    )

    import_proxy = (
        df["INTERCONNECTOR_DEPENDENCY"]
    )

    df["CARBON_INTENSITY_SCORE"] = (

        0.5 * renewable_component

        +

        0.3 * gas_proxy

        +

        0.2 * import_proxy

    )

    return df


# =========================================================
# CLEAN FEATURE STORE
# =========================================================

def finalize_dataset(df):

    print("\nFinalizing feature store...")

    # =====================================================
    # HANDLE INFINITE VALUES
    # =====================================================

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # =====================================================
    # FILL NA
    # =====================================================

    df = df.bfill().ffill()

    # =====================================================
    # FINAL DROP
    # =====================================================

    df = df.dropna()

    print(
        f"Final dataset shape: {df.shape}"
    )

    return df


# =========================================================
# SAVE FEATURE STORE
# =========================================================

def save_feature_store(df):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nFeature store saved:\n{OUTPUT_FILE}"
    )


# =========================================================
# MAIN PIPELINE
# =========================================================

def run_feature_engineering():

    print("\n===================================")

    print("GRIDFLEX AI FEATURE ENGINEERING")

    print("===================================")

    df = load_data()

    df = create_time_features(df)

    df = create_demand_features(df)

    df = create_renewable_features(df)

    df = create_interconnector_features(df)

    df = create_storage_features(df)

    df = create_transfer_features(df)

    df = create_market_features(df)

    df = create_carbon_features(df)

    df = finalize_dataset(df)

    save_feature_store(df)

    print("\nFeature engineering complete.")

    return df


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_feature_engineering()