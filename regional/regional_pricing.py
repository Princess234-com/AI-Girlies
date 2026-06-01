# ======================================================
# GRIDFLEX AI — REGIONAL PRICING ENGINE
# ======================================================
# File: regional/regional_pricing.py
#
# PURPOSE:
# Generates realistic regional electricity prices
# using:
#
# - regional demand
# - renewable availability
# - congestion
# - time-of-day behaviour
# - market volatility
# - interconnector influence
# - carbon intensity
#
# IMPORTANT:
# Pricing is NOT directly proportional to demand.
#
# This script intentionally separates:
#
# GRID STATE:
# - ND
# - renewables
# - flows
#
# FROM:
#
# MARKET STATE:
# - congestion
# - tariffs
# - volatility
# - carbon pricing
#
# This is academically important.
#
# OUTPUT:
# data/processed/regional_pricing_dataset.csv
#
# ======================================================

import numpy as np
import pandas as pd

from regional.regional_config import (
    REGIONAL_CONFIG
)

from config import (
    PROCESSED_DATA_DIR,
    RANDOM_SEED
)


# ======================================================
# FILE PATHS
# ======================================================

INPUT_FILE = (
    f"{PROCESSED_DATA_DIR}/"
    "regional_demand_dataset.csv"
)

OUTPUT_FILE = (
    f"{PROCESSED_DATA_DIR}/"
    "regional_pricing_dataset.csv"
)


# ======================================================
# RANDOM SEED
# ======================================================

np.random.seed(RANDOM_SEED)


# ======================================================
# LOAD DATA
# ======================================================

def load_data():

    print(
        "\nLoading regional demand dataset..."
    )

    df = pd.read_csv(INPUT_FILE)

    # ==================================================
    # TIMESTAMP
    # ==================================================

    if "TIMESTAMP" in df.columns:

        df["TIMESTAMP"] = pd.to_datetime(
            df["TIMESTAMP"]
        )

    elif "FULL_TIMESTAMP" in df.columns:

        df["TIMESTAMP"] = pd.to_datetime(
            df["FULL_TIMESTAMP"]
        )

    else:

        raise ValueError(
            "TIMESTAMP column missing."
        )

    return df


# ======================================================
# CREATE TIME FEATURES
# ======================================================

def create_time_features(df):

    print(
        "\nCreating pricing time features..."
    )

    df["HOUR"] = (
        df["TIMESTAMP"]
        .dt.hour
    )

    df["MONTH"] = (
        df["TIMESTAMP"]
        .dt.month
    )

    df["DAY_OF_WEEK"] = (
        df["TIMESTAMP"]
        .dt.dayofweek
    )

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"] >= 5
    ).astype(int)

    return df


# ======================================================
# CREATE RENEWABLE RATIO
# ======================================================

def create_renewable_ratio(df):

    print(
        "\nCreating renewable ratios..."
    )

    renewable_generation = (

        df["EMBEDDED_WIND_GENERATION"]

        +

        df["EMBEDDED_SOLAR_GENERATION"]

    )

    renewable_capacity = (

        df["EMBEDDED_WIND_CAPACITY"]

        +

        df["EMBEDDED_SOLAR_CAPACITY"]

    )

    df["RENEWABLE_RATIO"] = (

        renewable_generation

        /

        renewable_capacity.clip(lower=1)

    )

    df["RENEWABLE_RATIO"] = (

        df["RENEWABLE_RATIO"]

        .clip(0, 1)

    )

    return df


# ======================================================
# CREATE INTERCONNECTOR FACTOR
# ======================================================

def create_interconnector_factor(df):

    print(
        "\nCalculating interconnector influence..."
    )

    interconnector_columns = [

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

    available_columns = [

        col for col in interconnector_columns

        if col in df.columns

    ]

    if len(available_columns) == 0:

        df["INTERCONNECTOR_FACTOR"] = 0

        return df

    total_flow = df[
        available_columns
    ].sum(axis=1)

    normalized_flow = (

        total_flow

        /

        total_flow.abs().max()

    )

    df["INTERCONNECTOR_FACTOR"] = (
        normalized_flow.fillna(0)
    )

    return df


# ======================================================
# CREATE CARBON INTENSITY
# ======================================================

def create_carbon_intensity(df):

    print(
        "\nGenerating carbon intensity..."
    )

    df["CARBON_INTENSITY"] = (

        1

        -

        (
            df["RENEWABLE_RATIO"]
        )

    )

    df["CARBON_INTENSITY"] = (
        df["CARBON_INTENSITY"]
        .clip(0, 1)
    )

    return df


# ======================================================
# PEAK PERIOD MULTIPLIER
# ======================================================

def calculate_peak_multiplier(hour):

    # ----------------------------------------------
    # Morning Peak
    # ----------------------------------------------

    if 6 <= hour <= 9:

        return 1.12

    # ----------------------------------------------
    # Evening Peak
    # ----------------------------------------------

    elif 16 <= hour <= 20:

        return 1.22

    # ----------------------------------------------
    # Overnight Low
    # ----------------------------------------------

    elif 0 <= hour <= 5:

        return 0.82

    return 1.0


# ======================================================
# WEEKEND MULTIPLIER
# ======================================================

def calculate_weekend_multiplier(is_weekend):

    return 0.94 if is_weekend else 1.0


# ======================================================
# GENERATE REGIONAL PRICES
# ======================================================

def generate_regional_prices(df):

    print(
        "\nGenerating regional pricing..."
    )

    for region_name, config in (
        REGIONAL_CONFIG.items()
    ):

        print(
            f"Creating prices for {region_name}..."
        )

        # ==================================================
        # REGIONAL DEMAND
        # ==================================================

        demand_col = (
            f"{region_name}_DEMAND"
        )

        regional_demand = df[demand_col]

        demand_pressure = (

            regional_demand

            /

            regional_demand.max()

        )

        # ==================================================
        # RENEWABLE EFFECT
        # ==================================================

        renewable_effect = (

            df["RENEWABLE_RATIO"]

            *

            config.renewable_factor

        )

        # ==================================================
        # CARBON EFFECT
        # ==================================================

        carbon_effect = (

            df["CARBON_INTENSITY"]

            *

            config.carbon_intensity_factor

        )

        # ==================================================
        # INTERCONNECTOR EFFECT
        # ==================================================

        interconnector_effect = (

            1

            -

            (
                df["INTERCONNECTOR_FACTOR"]
                * 0.08
            )

        )

        # ==================================================
        # TIME-OF-DAY EFFECT
        # ==================================================

        peak_effect = df["HOUR"].apply(
            calculate_peak_multiplier
        )

        # ==================================================
        # WEEKEND EFFECT
        # ==================================================

        weekend_effect = df[
            "IS_WEEKEND"
        ].apply(
            calculate_weekend_multiplier
        )

        # ==================================================
        # RANDOM MARKET VOLATILITY
        # ==================================================

        market_noise = np.random.normal(

            loc=0,

            scale=config.volatility,

            size=len(df)

        )

        # ==================================================
        # BASE PRICE
        # ==================================================

        base_price = 68

        # ==================================================
        # FINAL PRICE MODEL
        # ==================================================

        regional_price = (

            base_price

            *

            (
                1
                +
                (demand_pressure * 0.45)
            )

            *

            config.price_multiplier

            *

            config.congestion_factor

            *

            peak_effect

            *

            weekend_effect

            *

            (
                1
                +
                (carbon_effect * 0.15)
            )

            *

            (
                1
                -
                (renewable_effect * 0.28)
            )

            *

            interconnector_effect

            *

            (
                1
                +
                market_noise
            )

        )

        # ==================================================
        # SAFETY CLIP
        # ==================================================

        regional_price = (
            regional_price
            .clip(lower=15)
        )

        # ==================================================
        # SAVE
        # ==================================================

        df[
            f"{region_name}_PRICE"
        ] = regional_price.round(2)

    return df


# ======================================================
# NATIONAL PRICE INDEX
# ======================================================

def create_national_price_index(df):

    print(
        "\nCreating national price index..."
    )

    regional_price_columns = [

        f"{region}_PRICE"

        for region in REGIONAL_CONFIG.keys()

    ]

    df["NATIONAL_PRICE"] = (

        df[regional_price_columns]

        .mean(axis=1)

        .round(2)

    )

    return df


# ======================================================
# DISPLAY SUMMARY
# ======================================================

def display_summary(df):

    print("\n====================================")
    print("REGIONAL PRICING SUMMARY")
    print("====================================")

    for region_name in REGIONAL_CONFIG.keys():

        price_col = (
            f"{region_name}_PRICE"
        )

        print(f"\n{region_name}")

        print(
            f"Average Price: £"
            f"{round(df[price_col].mean(), 2)}"
        )

        print(
            f"Peak Price: £"
            f"{round(df[price_col].max(), 2)}"
        )

        print(
            f"Minimum Price: £"
            f"{round(df[price_col].min(), 2)}"
        )

    print("\nNational Price")

    print(
        f"Average: £"
        f"{round(df['NATIONAL_PRICE'].mean(), 2)}"
    )


# ======================================================
# SAVE DATA
# ======================================================

def save_data(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nRegional pricing dataset saved:\n"
        f"{OUTPUT_FILE}"
    )


# ======================================================
# MAIN PIPELINE
# ======================================================

def run_regional_pricing_pipeline():

    print("\n====================================")
    print("GRIDFLEX AI REGIONAL PRICING ENGINE")
    print("====================================")

    # ==================================================
    # LOAD
    # ==================================================

    df = load_data()

    # ==================================================
    # FEATURES
    # ==================================================

    df = create_time_features(df)

    df = create_renewable_ratio(df)

    df = create_interconnector_factor(df)

    df = create_carbon_intensity(df)

    # ==================================================
    # PRICING
    # ==================================================

    df = generate_regional_prices(df)

    # ==================================================
    # NATIONAL INDEX
    # ==================================================

    df = create_national_price_index(df)

    # ==================================================
    # SUMMARY
    # ==================================================

    display_summary(df)

    # ==================================================
    # SAVE
    # ==================================================

    save_data(df)

    print(
        "\nRegional pricing generation complete."
    )

    return df


# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":

    run_regional_pricing_pipeline()