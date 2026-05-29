from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    PREDICTIONS_DIR,
    REGIONAL_SETTINGS,
    RANDOM_SEED,
)


# ======================================================
# RANDOM SEED
# ======================================================

np.random.seed(RANDOM_SEED)


# ======================================================
# DATASET PATHS
# ======================================================

RAW_DEMAND_FILE = (
    RAW_DATA_DIR
    / "national_grid_historic_demand.csv"
)

CENTRALIZED_OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "centralized_energy_dataset.csv"
)


# ======================================================
# REQUIRED COLUMNS
# ======================================================

REQUIRED_COLUMNS = [
    "SETTLEMENT_DATE",
    "SETTLEMENT_PERIOD",
    "ND",
    "TSD",
    "EMBEDDED_WIND_GENERATION",
    "EMBEDDED_WIND_CAPACITY",
    "EMBEDDED_SOLAR_GENERATION",
    "EMBEDDED_SOLAR_CAPACITY",
    "BRITNED_FLOW",
    "MOYLE_FLOW",
    "EAST_WEST_FLOW",
    "NEMO_FLOW",
    "NSL_FLOW",
    "ELECLINK_FLOW",
    "VIKING_FLOW",
    "GREENLINK_FLOW",
]


# ======================================================
# CREATE DIRECTORIES
# ======================================================


def ensure_directories():
    """Ensure all required directories exist."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)


# ======================================================
# LOAD RAW DATA
# ======================================================


def load_raw_dataset(
    filepath: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Load raw NESO / National Grid dataset.
    """

    if filepath is None:
        filepath = RAW_DEMAND_FILE

    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{filepath}"
        )

    print("Loading raw national demand dataset...")

    df = pd.read_csv(filepath)

    print(f"Loaded rows: {len(df):,}")

    return df


# ======================================================
# VALIDATE DATASET
# ======================================================


def validate_dataset(df: pd.DataFrame):
    """
    Validate required columns.
    """

    missing_columns = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if len(missing_columns) > 0:
        raise ValueError(
            f"Missing required columns:\n{missing_columns}"
        )

    print("Dataset validation successful.")


# ======================================================
# CREATE TIMESTAMP
# ======================================================


def create_timestamp(df: pd.DataFrame):
    """
    Create half-hour timestamp.
    """

    print("Creating timestamps...")

    df["SETTLEMENT_DATE"] = pd.to_datetime(
        df["SETTLEMENT_DATE"]
    )

    settlement_offset = (
        df["SETTLEMENT_PERIOD"] - 1
    ) * 30

    df["TIMESTAMP"] = (
        df["SETTLEMENT_DATE"]
        + pd.to_timedelta(
            settlement_offset,
            unit="m"
        )
    )

    return df


# ======================================================
# SORT DATA
# ======================================================


def sort_dataset(df: pd.DataFrame):
    """
    Sort chronologically.
    """

    df = df.sort_values("TIMESTAMP")

    df = df.reset_index(drop=True)

    return df


# ======================================================
# HANDLE MISSING VALUES
# ======================================================


def handle_missing_values(df: pd.DataFrame):
    """
    Fill missing values safely.
    """

    print("Handling missing values...")

    numeric_columns = df.select_dtypes(
        include=[np.number]
    ).columns

    for col in numeric_columns:
        df[col] = (
            df[col]
            .interpolate(method="linear")
            .bfill()
            .ffill()
        )

    return df


# ======================================================
# RENEWABLE FEATURES
# ======================================================


def create_renewable_features(df: pd.DataFrame):
    """
    Renewable generation calculations.
    """

    print("Creating renewable features...")

    df["TOTAL_RENEWABLE_GENERATION"] = (
        df["EMBEDDED_WIND_GENERATION"]
        + df["EMBEDDED_SOLAR_GENERATION"]
    )

    df["TOTAL_RENEWABLE_CAPACITY"] = (
        df["EMBEDDED_WIND_CAPACITY"]
        + df["EMBEDDED_SOLAR_CAPACITY"]
    )

    df["RENEWABLE_RATIO"] = (
        df["TOTAL_RENEWABLE_GENERATION"]
        /
        (
            df["ND"] + 1
        )
    )

    df["RENEWABLE_UTILIZATION"] = (
        df["TOTAL_RENEWABLE_GENERATION"]
        /
        (
            df["TOTAL_RENEWABLE_CAPACITY"] + 1
        )
    )

    df["RENEWABLE_RATIO"] = (
        df["RENEWABLE_RATIO"]
        .clip(0, 1)
    )

    return df


# ======================================================
# INTERCONNECTOR FEATURES
# ======================================================


def create_interconnector_features(df: pd.DataFrame):
    """
    Aggregate interconnector flows.
    """

    print("Creating interconnector features...")

    interconnector_columns = [
        "BRITNED_FLOW",
        "MOYLE_FLOW",
        "EAST_WEST_FLOW",
        "NEMO_FLOW",
        "NSL_FLOW",
        "ELECLINK_FLOW",
        "VIKING_FLOW",
        "GREENLINK_FLOW",
    ]

    existing_columns = [
        col
        for col in interconnector_columns
        if col in df.columns
    ]

    df["TOTAL_INTERCONNECTOR_FLOW"] = (
        df[existing_columns]
        .sum(axis=1)
    )

    return df


# ======================================================
# GRID STRESS SCORE
# ======================================================


def create_grid_stress_score(df: pd.DataFrame):
    """
    Create normalized grid stress metric.
    """

    print("Creating grid stress score...")

    demand_component = (
        df["ND"]
        /
        df["ND"].max()
    )

    renewable_component = (
        1 - df["RENEWABLE_RATIO"]
    )

    interconnector_component = (
        abs(df["TOTAL_INTERCONNECTOR_FLOW"])
        /
        (
            abs(
                df["TOTAL_INTERCONNECTOR_FLOW"]
            ).max()
            + 1
        )
    )

    stress_score = (
        (0.50 * demand_component)
        +
        (0.30 * renewable_component)
        +
        (0.20 * interconnector_component)
    )

    df["GRID_STRESS_SCORE"] = (
        stress_score.clip(0, 1)
    )

    return df


# ======================================================
# CARBON INTENSITY ESTIMATION
# ======================================================


def create_carbon_intensity(df: pd.DataFrame):
    """
    Synthetic carbon intensity estimate.
    """

    print("Creating carbon intensity...")

    demand_pressure = (
        df["ND"]
        /
        df["ND"].max()
    )

    renewable_factor = (
        1 - df["RENEWABLE_RATIO"]
    )

    carbon_intensity = (
        150
        +
        (220 * demand_pressure)
        +
        (180 * renewable_factor)
    )

    df["CARBON_INTENSITY"] = carbon_intensity

    return df


# ======================================================
# TIME FEATURES
# ======================================================


def create_time_features(df: pd.DataFrame):
    """
    Create time-based ML features.
    """

    print("Creating time features...")

    df["YEAR"] = df["TIMESTAMP"].dt.year
    df["MONTH"] = df["TIMESTAMP"].dt.month
    df["DAY"] = df["TIMESTAMP"].dt.day
    df["DAY_OF_WEEK"] = df["TIMESTAMP"].dt.dayofweek
    df["HOUR"] = df["TIMESTAMP"].dt.hour
    df["MINUTE"] = df["TIMESTAMP"].dt.minute

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"] >= 5
    ).astype(int)

    return df


# ======================================================
# LAG FEATURES
# ======================================================


def create_lag_features(df: pd.DataFrame):
    """
    Create forecasting lag variables.
    """

    print("Creating lag features...")

    lag_periods = [
        1,
        2,
        48,
        96,
    ]

    for lag in lag_periods:
        df[f"ND_LAG_{lag}"] = (
            df["ND"].shift(lag)
        )

    rolling_windows = [
        6,
        12,
        48,
    ]

    for window in rolling_windows:
        df[f"ND_ROLLING_MEAN_{window}"] = (
            df["ND"]
            .rolling(window=window)
            .mean()
        )

    df = df.bfill()

    return df


# ======================================================
# REGIONAL FEATURES
# ======================================================


def create_regional_features(df: pd.DataFrame):
    """
    Generate semi-independent regional demand.
    """

    print("Creating regional features...")

    for region_name, config in REGIONAL_SETTINGS.items():

        demand_weight = config[
            "demand_weight"
        ]

        economic_factor = config[
            "economic_factor"
        ]

        renewable_factor = config[
            "renewable_factor"
        ]

        volatility = config[
            "volatility"
        ]

        noise = np.random.normal(
            loc=0,
            scale=volatility,
            size=len(df)
        )

        seasonal_component = (
            0.04
            *
            np.sin(
                2
                *
                np.pi
                *
                np.arange(len(df))
                /
                48
            )
        )

        regional_demand = (
            df["ND"]
            *
            demand_weight
            *
            economic_factor
            *
            (
                1
                + noise
                + seasonal_component
            )
        )

        regional_demand = (
            regional_demand.clip(lower=0)
        )

        regional_price = (
            55
            *
            config["price_multiplier"]
            *
            (
                1
                + (
                    regional_demand
                    /
                    (regional_demand.max() + 1)
                )
            )
            *
            (
                1
                - (
                    df["RENEWABLE_RATIO"]
                    * renewable_factor
                    * 0.25
                )
            )
            *
            (
                1 + noise
            )
        )

        regional_price = (
            regional_price.clip(lower=20)
        )

        df[f"{region_name}_DEMAND"] = regional_demand
        df[f"{region_name}_PRICE"] = regional_price

    return df


# ======================================================
# SAVE DATASET
# ======================================================


def save_dataset(df: pd.DataFrame):
    """
    Save centralized dataset.
    """

    df.to_csv(
        CENTRALIZED_OUTPUT_FILE,
        index=False
    )

    print(
        f"\nCentralized dataset saved:\n"
        f"{CENTRALIZED_OUTPUT_FILE}"
    )


# ======================================================
# MAIN PIPELINE
# ======================================================


def build_centralized_dataset():
    """
    Full centralized preprocessing pipeline.
    """

    ensure_directories()

    df = load_raw_dataset()

    validate_dataset(df)

    df = create_timestamp(df)

    df = sort_dataset(df)

    df = handle_missing_values(df)

    df = create_renewable_features(df)

    df = create_interconnector_features(df)

    df = create_grid_stress_score(df)

    df = create_carbon_intensity(df)

    df = create_time_features(df)

    df = create_lag_features(df)

    df = create_regional_features(df)

    save_dataset(df)

    print("\nCentralized dataset pipeline complete.")

    return df


# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":

    dataset = build_centralized_dataset()

    print(dataset.head())

