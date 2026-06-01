from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    RANDOM_SEED,
    REGIONAL_SETTINGS,
    PROCESSED_DATA_DIR,
)


from config import (
    GRID_STRESS_DATASET_PATH,
    PRICING_DATASET_PATH,
    RANDOM_SEED,
    REGIONAL_SETTINGS,
)

INPUT_FILE = GRID_STRESS_DATASET_PATH
OUTPUT_FILE = PRICING_DATASET_PATH

np.random.seed(RANDOM_SEED)



def load_dataset():

    print("Loading grid stress dataset...")

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Grid stress dataset not found:\n{INPUT_FILE}\n"
           
        )

    df = pd.read_csv(INPUT_FILE)

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"]
    )

    if (
        "CARBON_INTENSITY" not in df.columns
        and
        "CARBON_INTENSITY_SCORE" in df.columns
    ):
        df["CARBON_INTENSITY"] = df[
            "CARBON_INTENSITY_SCORE"
        ]

    return df




def normalize(series):

    denominator = (
        series.max() - series.min()
    )

    if denominator == 0:

        return pd.Series(
            np.zeros(len(series))
        )

    return (

        (series - series.min())

        /

        denominator

    )



def generate_market_volatility(

    size,
    scale=0.04

):

    return np.random.normal(

        loc=0,

        scale=scale,

        size=size

    )



def create_time_of_day_multiplier(df):

    hour = df["HOUR"]

    multiplier = np.select(

        [

            # Overnight cheap
            (
                (hour >= 0)
                &
                (hour <= 5)
            ),

            # Morning rise
            (
                (hour >= 6)
                &
                (hour <= 9)
            ),

            # Daytime moderate
            (
                (hour >= 10)
                &
                (hour <= 15)
            ),

            # Evening peak
            (
                (hour >= 16)
                &
                (hour <= 20)
            ),

            # Late evening
            (
                (hour >= 21)
                &
                (hour <= 23)
            )

        ],

        [

            0.82,
            1.08,
            0.95,
            1.30,
            1.00

        ],

        default=1.0

    )

    return multiplier




def create_carbon_price_signal(df):

    carbon_norm = normalize(
        df["CARBON_INTENSITY"]
    )

    carbon_multiplier = (

        1
        +
        (
            carbon_norm * 0.18
        )

    )

    return carbon_multiplier




def create_renewable_discount(df):

    renewable_discount = (

        1
        -
        (
            df["RENEWABLE_RATIO"]
            * 0.25
        )

    )

    return renewable_discount




def create_congestion_signal(df):

    congestion = normalize(
        abs(
            df[
                "TOTAL_INTERCONNECTOR_FLOW"
            ]
        )
    )

    congestion_multiplier = (

        1
        +
        (
            congestion * 0.15
        )

    )

    return congestion_multiplier



def create_market_demand_signal(df):

    demand_norm = normalize(
        df["ND"]
    )

    market_signal = (

        1
        +
        (
            demand_norm * 0.35
        )

    )

    return market_signal



def create_national_price(df):

    print(
        "\nGenerating national pricing..."
    )

    base_price = 58

    time_multiplier = (
        create_time_of_day_multiplier(df)
    )

    carbon_multiplier = (
        create_carbon_price_signal(df)
    )

    renewable_discount = (
        create_renewable_discount(df)
    )

    congestion_multiplier = (
        create_congestion_signal(df)
    )

    market_signal = (
        create_market_demand_signal(df)
    )

    volatility = generate_market_volatility(
        len(df),
        scale=0.05
    )

    price = (

        base_price

        *

        market_signal

        *

        time_multiplier

        *

        carbon_multiplier

        *

        congestion_multiplier

        *

        renewable_discount

        *

        (
            1 + volatility
        )

    )

    price = price.clip(lower=20)

    df["NATIONAL_PRICE"] = (
        price.round(2)
    )

    return df




def create_regional_prices(df):

    print(
        "\nGenerating regional prices..."
    )

    for region_name, config in REGIONAL_SETTINGS.items():

        print(
            f"Creating {region_name} pricing..."
        )

        regional_demand_col = (
            f"{region_name}_DEMAND"
        )

        demand_signal = normalize(
            df[regional_demand_col]
        )

        regional_market_pressure = (

            1
            +
            (
                demand_signal * 0.25
            )

        )

        regional_volatility = (
            generate_market_volatility(

                len(df),

                scale=config[
                    "volatility"
                ]

            )
        )

        regional_price = (

            df["NATIONAL_PRICE"]

            *

            config[
                "price_multiplier"
            ]

            *

            config[
                "congestion_factor"
            ]

            *

            regional_market_pressure

            *

            (
                1
                -
                (
                    df[
                        "RENEWABLE_RATIO"
                    ]

                    *

                    config[
                        "renewable_factor"
                    ]

                    *

                    0.12
                )
            )

            *

            (
                1
                +
                regional_volatility
            )

        )

        regional_price = (
            regional_price.clip(lower=15)
        )

        df[
            f"{region_name}_PRICE"
        ] = regional_price.round(2)

    return df




def create_market_state_variables(df):

    print(
        "\nCreating market state variables..."
    )

    df["MARKET_VOLATILITY_INDEX"] = (
        normalize(
            abs(
                generate_market_volatility(
                    len(df),
                    scale=0.12
                )
            )
        )
    )

    df["TIME_OF_USE_SIGNAL"] = (
        create_time_of_day_multiplier(df)
    )

    df["MARKET_CONGESTION_INDEX"] = (
        create_congestion_signal(df)
    )

    df["CARBON_PRICE_SIGNAL"] = (
        create_carbon_price_signal(df)
    )

    return df



def create_price_categories(df):

    print(
        "\nCreating price categories..."
    )

    q1 = df[
        "NATIONAL_PRICE"
    ].quantile(0.25)

    q2 = df[
        "NATIONAL_PRICE"
    ].quantile(0.50)

    q3 = df[
        "NATIONAL_PRICE"
    ].quantile(0.75)

    def classify(price):

        if price <= q1:
            return "Very Low"

        elif price <= q2:
            return "Low"

        elif price <= q3:
            return "Moderate"

        else:
            return "High"

    df["PRICE_CATEGORY"] = (
        df["NATIONAL_PRICE"]
        .apply(classify)
    )

    return df


#display

def display_summary(df):


    print(
        "GRIDFLEX AI PRICING SUMMARY"
    )



    print(
        f"\nAverage National Price:"
    )

    print(
        f"£{round(df['NATIONAL_PRICE'].mean(), 2)}"
    )

    print(
        f"\nMaximum National Price:"
    )

    print(
        f"£{round(df['NATIONAL_PRICE'].max(), 2)}"
    )

    print(
        f"\nMinimum National Price:"
    )

    print(
        f"£{round(df['NATIONAL_PRICE'].min(), 2)}"
    )

    print("\nRegional Pricing:")
    print(
        "Regional prices are generated separately "
        "by regional/regional_pricing.py"
    )

#save dataset

def save_dataset(df):

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nPricing dataset saved:\n"
        f"{OUTPUT_FILE}"
    )



def run_pricing_pipeline():

    df = load_dataset()

    df = create_national_price(df)

    #df = create_regional_prices(df)

    df = create_market_state_variables(df)

    df = create_price_categories(df)

    save_dataset(df)

    display_summary(df)

    print(
        "\nPricing pipeline complete."
    )

    return df


#run

if __name__ == "__main__":

    pricing_df = (
        run_pricing_pipeline()
    )

    print(
        pricing_df.head()
    )