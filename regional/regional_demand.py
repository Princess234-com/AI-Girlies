import numpy as np
import pandas as pd


from config import (
    REGIONAL_SETTINGS,
    PROCESSED_DATA_DIR,
    RANDOM_SEED
)


INPUT_FILE = (
    f"{PROCESSED_DATA_DIR}/"
    "master_energy_dataset.csv"
)

OUTPUT_FILE = (
    f"{PROCESSED_DATA_DIR}/"
    "regional_demand_dataset.csv"
)


np.random.seed(RANDOM_SEED)



def load_data():

    print(
        "\nLoading master dataset..."
    )

    df = pd.read_csv(INPUT_FILE)


    if "TIMESTAMP" not in df.columns:

        if "FULL_TIMESTAMP" in df.columns:

            df["TIMESTAMP"] = pd.to_datetime(
                df["FULL_TIMESTAMP"]
            )

        else:

            raise ValueError(
                "TIMESTAMP column missing."
            )

    else:

        df["TIMESTAMP"] = pd.to_datetime(
            df["TIMESTAMP"]
        )


    required_columns = [

        "ND",
        "EMBEDDED_WIND_GENERATION",
        "EMBEDDED_SOLAR_GENERATION"

    ]

    missing = [

        col for col in required_columns

        if col not in df.columns

    ]

    if len(missing) > 0:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    return df



def create_time_features(df):

    print(
        "\nCreating time features..."
    )

    df["HOUR"] = (
        df["TIMESTAMP"]
        .dt.hour
    )

    df["DAY_OF_WEEK"] = (
        df["TIMESTAMP"]
        .dt.dayofweek
    )

    df["MONTH"] = (
        df["TIMESTAMP"]
        .dt.month
    )

    df["DAY_OF_YEAR"] = (
        df["TIMESTAMP"]
        .dt.dayofyear
    )

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"] >= 5
    ).astype(int)

    return df


def create_daily_seasonality(df):

    return (

        0.04

        *

        np.sin(

            2
            * np.pi
            * df["HOUR"]
            / 24

        )

    )


def create_weekly_seasonality(df):

    return (

        0.03

        *

        np.cos(

            2
            * np.pi
            * df["DAY_OF_WEEK"]
            / 7

        )

    )



def create_yearly_seasonality(df):

    return (

        0.06

        *

        np.sin(

            2
            * np.pi
            * df["DAY_OF_YEAR"]
            / 365

        )

    )


def generate_regional_demands(df):

    print(
        "\nGenerating regional demands..."
    )

    national_demand = df["ND"]


    daily_pattern = create_daily_seasonality(df)

    weekly_pattern = create_weekly_seasonality(df)

    yearly_pattern = create_yearly_seasonality(df)

    for region_name, config in REGIONAL_SETTINGS.items():

        print(
            f"Generating {region_name}..."
        )


        base_weight = (
            config["demand_weight"]
        )


        stochastic_noise = np.random.normal(

            loc=0,

            scale=0.025,

            size=len(df)

        )


        economic_component = (
            config["economic_factor"]
        )


        renewable_component = (

            (
                df[
                    "EMBEDDED_WIND_GENERATION"
                ]

                +

                df[
                    "EMBEDDED_SOLAR_GENERATION"
                ]

            )

            /

            national_demand.clip(lower=1)

        )

        renewable_component = (

            renewable_component

            *

            config["renewable_factor"]

            *

            0.08

        )


        weekend_adjustment = np.where(

            df["IS_WEEKEND"] == 1,

            -0.03,

            0.02

        )


        regional_demand = (

            national_demand

            *

            base_weight

            *

            economic_component

            *

            (

                1

                +

                daily_pattern

                +

                weekly_pattern

                +

                yearly_pattern

                +

                renewable_component

                +

                stochastic_noise

                +

                weekend_adjustment

            )

        )

        regional_demand = (
            regional_demand
            .clip(lower=0)
        )


        df[
            f"{region_name}_DEMAND"
        ] = regional_demand.round(2)

    return df


def generate_regional_stress(df):

    print(
        "\nGenerating regional stress scores..."
    )

    for region_name in REGIONAL_SETTINGS.keys():

        demand_col = (
            f"{region_name}_DEMAND"
        )

        stress_col = (
            f"{region_name}_GRID_STRESS"
        )

        regional_max = (
            df[demand_col].max()
        )

        stress_score = (

            df[demand_col]

            /

            regional_max

        )

        stress_score = (
            stress_score
            .clip(0, 1)
        )

        df[stress_col] = (
            stress_score.round(4)
        )

    return df


def display_summary(df):

    print("REGIONAL DEMAND SUMMARY")


    for region_name in REGIONAL_SETTINGS.keys():

        demand_col = (
            f"{region_name}_DEMAND"
        )

        stress_col = (
            f"{region_name}_GRID_STRESS"
        )

        print(f"\n{region_name}")

        print(
            f"Average Demand: "
            f"{round(df[demand_col].mean(), 2)} MW"
        )

        print(
            f"Peak Demand: "
            f"{round(df[demand_col].max(), 2)} MW"
        )

        print(
            f"Average Stress: "
            f"{round(df[stress_col].mean(), 3)}"
        )


def save_data(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nRegional dataset saved:\n"
        f"{OUTPUT_FILE}"
    )

def run_regional_demand_pipeline():


    print("GRIDFLEX AI REGIONAL DEMAND ENGINE")


    df = load_data()


    df = create_time_features(df)

    df = generate_regional_demands(df)


    df = generate_regional_stress(df)

    display_summary(df)


    save_data(df)

    print(
        "\nRegional demand generation complete."
    )

    return df



if __name__ == "__main__":

    run_regional_demand_pipeline()