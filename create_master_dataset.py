import pandas as pd
import numpy as np

from config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR
)


# ======================================================
# FILE PATHS
# ======================================================

RAW_FILE_PATTERN = "demanddata_*.csv"

OUTPUT_FILE = (
    f"{PROCESSED_DATA_DIR}/"
    "master_energy_dataset.csv"
)


# ======================================================
# LOAD RAW DATA
# ======================================================

def load_raw_dataset():

    print(
        "\nLoading raw NESO yearly datasets..."
    )

    files = sorted(
        RAW_DATA_DIR.glob(
            RAW_FILE_PATTERN
        )
    )

    if len(files) == 0:

        raise FileNotFoundError(
            f"No raw demand files found:\n"
            f"{RAW_DATA_DIR}"
        )

    all_dfs = []

    for file in files:

        print(
            f"Loading {file.name}..."
        )

        temp_df = pd.read_csv(
            file
        )

        temp_df[
            "SOURCE_FILE"
        ] = file.name

        all_dfs.append(
            temp_df
        )

    df = pd.concat(

        all_dfs,

        ignore_index=True

    )

    print(
        f"\nCombined rows loaded: "
        f"{len(df):,}"
    )

    return df



# ======================================================
# STANDARDIZE COLUMNS
# ======================================================

def standardize_columns(df):

    print(
        "\nStandardizing columns..."
    )

    df.columns = [

        col.strip().upper()

        for col in df.columns

    ]

    return df


# ======================================================
# CREATE TIMESTAMP
# ======================================================

def create_timestamp(df):

    print(
        "\nCreating timestamps..."
    )

    # ==================================================
    # USE FULL_TIMESTAMP IF AVAILABLE
    # ==================================================

    if "FULL_TIMESTAMP" in df.columns:

        df["TIMESTAMP"] = pd.to_datetime(
            df["FULL_TIMESTAMP"]
        )

    # ==================================================
    # OTHERWISE BUILD FROM DATE + PERIOD
    # ==================================================

    elif (

        "SETTLEMENT_DATE" in df.columns

        and

        "SETTLEMENT_PERIOD" in df.columns

    ):

        df["SETTLEMENT_DATE"] = pd.to_datetime(
            df["SETTLEMENT_DATE"]
        )

        df["TIMESTAMP"] = (

            df["SETTLEMENT_DATE"]

            +

            pd.to_timedelta(

                (
                    df["SETTLEMENT_PERIOD"] - 1
                ) * 30,

                unit="minutes"

            )

        )

    else:

        raise ValueError(
            "No valid timestamp source found."
        )

    return df


# ======================================================
# REMOVE DUPLICATES
# ======================================================

def remove_duplicates(df):

    print(
        "\nRemoving duplicates..."
    )

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    print(
        f"Removed {before - after} duplicates."
    )

    return df


# ======================================================
# SORT DATA
# ======================================================

def sort_dataset(df):

    print(
        "\nSorting dataset..."
    )

    df = df.sort_values(
        "TIMESTAMP"
    )

    df = df.reset_index(
        drop=True
    )

    return df


# ======================================================
# HANDLE MISSING VALUES
# ======================================================

def handle_missing_values(df):

    print(
        "\nHandling missing values..."
    )

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    for column in numeric_columns:

        missing = df[column].isna().sum()

        if missing > 0:

            print(
                f"Filling missing values: "
                f"{column} ({missing})"
            )

            df[column] = (

                df[column]

                .interpolate(
                    method="linear"
                )

                .bfill()
                .ffill()

            )

    return df


# ======================================================
# CREATE TIME FEATURES
# ======================================================

def create_time_features(df):

    print(
        "\nCreating time features..."
    )

    df["YEAR"] = (
        df["TIMESTAMP"]
        .dt.year
    )

    df["MONTH"] = (
        df["TIMESTAMP"]
        .dt.month
    )

    df["DAY"] = (
        df["TIMESTAMP"]
        .dt.day
    )

    df["HOUR"] = (
        df["TIMESTAMP"]
        .dt.hour
    )

    df["MINUTE"] = (
        df["TIMESTAMP"]
        .dt.minute
    )

    df["DAY_OF_WEEK"] = (
        df["TIMESTAMP"]
        .dt.dayofweek
    )

    df["DAY_NAME"] = (
        df["TIMESTAMP"]
        .dt.day_name()
    )

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"] >= 5
    ).astype(int)

    return df


# ======================================================
# CREATE GRID STRESS SCORE
# ======================================================

def create_grid_stress_score(df):

    print(
        "\nCreating grid stress score..."
    )

    # ==================================================
    # NORMALIZED DEMAND
    # ==================================================

    normalized_demand = (

        df["ND"]

        /

        df["ND"].max()

    )

    # ==================================================
    # RENEWABLE CONTRIBUTION
    # ==================================================

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

    renewable_ratio = (

        renewable_generation

        /

        renewable_capacity.clip(lower=1)

    )

    renewable_ratio = (
        renewable_ratio
        .clip(0, 1)
    )

    # ==================================================
    # INTERCONNECTOR SUPPORT
    # ==================================================

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

    if len(available_columns) > 0:

        interconnector_support = (

            df[available_columns]

            .sum(axis=1)

            .abs()

        )

        interconnector_support = (

            interconnector_support

            /

            interconnector_support.max()

        )

    else:

        interconnector_support = 0

    # ==================================================
    # FINAL GRID STRESS
    # ==================================================

    grid_stress = (

        (normalized_demand * 0.70)

        +

        ((1 - renewable_ratio) * 0.20)

        +

        ((1 - interconnector_support) * 0.10)

    )

    grid_stress = (
        grid_stress
        .clip(0, 1)
    )

    df["GRID_STRESS_SCORE"] = (
        grid_stress.round(4)
    )

    df["RENEWABLE_RATIO"] = (
        renewable_ratio.round(4)
    )

    return df


# ======================================================
# VALIDATE REQUIRED COLUMNS
# ======================================================

def validate_dataset(df):

    print(
        "\nValidating dataset..."
    )

    required_columns = [

        "TIMESTAMP",
        "ND",
        "GRID_STRESS_SCORE",
        "RENEWABLE_RATIO"

    ]

    missing = [

        col for col in required_columns

        if col not in df.columns

    ]

    if len(missing) > 0:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print(
        "Dataset validation successful."
    )


# ======================================================
# DISPLAY SUMMARY
# ======================================================

def display_summary(df):

    print("\n===================================")
    print("MASTER DATASET SUMMARY")
    print("===================================")

    print(
        f"\nRows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"\nDate Range:"
    )

    print(
        f"{df['TIMESTAMP'].min()}"
    )

    print(
        f"to"
    )

    print(
        f"{df['TIMESTAMP'].max()}"
    )

    print(
        f"\nAverage Demand:"
    )

    print(
        f"{round(df['ND'].mean(), 2)} MW"
    )

    print(
        f"\nAverage Grid Stress:"
    )

    print(
        round(
            df["GRID_STRESS_SCORE"].mean(),
            3
        )
    )


# ======================================================
# SAVE DATASET
# ======================================================

def save_dataset(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nMaster dataset saved:\n"
        f"{OUTPUT_FILE}"
    )


# ======================================================
# MAIN PIPELINE
# ======================================================

# ======================================================
# MAIN PIPELINE
# ======================================================

def run_master_dataset_pipeline():

    print("\n===================================")
    print("GRIDFLEX AI MASTER DATASET ENGINE")
    print("===================================")

    df = load_raw_dataset()

    df = standardize_columns(df)
    df = create_timestamp(df)
    df = remove_duplicates(df)
    df = sort_dataset(df)
    df = handle_missing_values(df)

    df = create_time_features(df)
    df = create_grid_stress_score(df)

    validate_dataset(df)
    display_summary(df)
    save_dataset(df)

    print("\nMaster dataset pipeline complete.")

    return df


if __name__ == "__main__":

    run_master_dataset_pipeline()