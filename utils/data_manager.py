
import pandas as pd

from pathlib import Path

from config import (

    COLUMN_NAMES,

    CLEANED_DEMAND_FILE,

    REGIONAL_DEMAND_FILE,

    REGIONAL_PRICING_FILE,

    PRICING_MODEL_DATASET_FILE,

    FUTURE_FORECAST_FILE,

    OPTIMIZED_SCHEDULE_FILE

)

DATASET_REGISTRY = {

    "cleaned_demand":
    CLEANED_DEMAND_FILE,

    "regional_demand":
    REGIONAL_DEMAND_FILE,

    "regional_pricing":
    REGIONAL_PRICING_FILE,

    "pricing_model":
    PRICING_MODEL_DATASET_FILE,

    "future_forecast":
    FUTURE_FORECAST_FILE,

    "optimized_schedules":
    OPTIMIZED_SCHEDULE_FILE

}

def load_dataset(

    dataset_name,

    parse_dates=True,

    required_columns=None

):



    if dataset_name not in DATASET_REGISTRY:

        raise ValueError(
            f"Unknown dataset: {dataset_name}"
        )

    file_path = DATASET_REGISTRY[
        dataset_name
    ]

    if not Path(file_path).exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{file_path}"
        )

    print(
        f"\nLoading dataset:\n{file_path}"
    )

    df = pd.read_csv(file_path)


    timestamp_col = COLUMN_NAMES[
        "timestamp"
    ]

    if (

        parse_dates

        and

        timestamp_col in df.columns

    ):

        df[timestamp_col] = pd.to_datetime(

            df[timestamp_col],

            errors="coerce"

        )

    if required_columns is not None:

        validate_columns(

            df,

            required_columns

        )

    print(
        f"Loaded rows: {len(df)}"
    )

    return df

def save_dataset(

    df,

    dataset_name,

    index=False

):

  

    if dataset_name not in DATASET_REGISTRY:

        raise ValueError(
            f"Unknown dataset: {dataset_name}"
        )

    file_path = DATASET_REGISTRY[
        dataset_name
    ]


    Path(file_path).parent.mkdir(

        parents=True,

        exist_ok=True

    )


    df.to_csv(

        file_path,

        index=index

    )

    print(
        f"\nDataset saved:\n{file_path}"
    )



def validate_columns(

    df,

    required_columns

):



    missing = [

        col

        for col in required_columns

        if col not in df.columns

    ]

    if len(missing) > 0:

        raise ValueError(

            "\nMissing required columns:\n"

            f"{missing}"

        )



def standardize_timestamp_column(df):



    possible_columns = [

        "TIMESTAMP",

        "timestamp",

        "Datetime",

        "datetime",

        "FULL_TIMESTAMP"

    ]

    found = None

    for col in possible_columns:

        if col in df.columns:

            found = col
            break

    if found is None:

        raise ValueError(
            "No timestamp column found."
        )

    standardized_name = COLUMN_NAMES[
        "timestamp"
    ]

    df = df.rename(

        columns={
            found: standardized_name
        }

    )

    df[standardized_name] = pd.to_datetime(

        df[standardized_name],

        errors="coerce"

    )

    return df



def remove_duplicate_timestamps(df):



    timestamp_col = COLUMN_NAMES[
        "timestamp"
    ]

    before = len(df)

    df = df.drop_duplicates(

        subset=[timestamp_col]

    )

    after = len(df)

    removed = before - after

    print(
        f"Removed duplicates: {removed}"
    )

    return df



def sort_by_timestamp(df):



    timestamp_col = COLUMN_NAMES[
        "timestamp"
    ]

    return df.sort_values(
        timestamp_col
    ).reset_index(drop=True)



def add_time_features(df):


    timestamp_col = COLUMN_NAMES[
        "timestamp"
    ]

    if timestamp_col not in df.columns:

        raise ValueError(
            "TIMESTAMP column missing."
        )

    df["HOUR"] = (
        df[timestamp_col]
        .dt.hour
    )

    df["DAY_OF_WEEK"] = (
        df[timestamp_col]
        .dt.dayofweek
    )

    df["MONTH"] = (
        df[timestamp_col]
        .dt.month
    )

    df["IS_WEEKEND"] = (
        df["DAY_OF_WEEK"]
        >= 5
    ).astype(int)

    df["SETTLEMENT_PERIOD"] = (

        (
            df["HOUR"]
            * 2
        )

        +

        (
            df[timestamp_col]
            .dt.minute
            // 30
        )

        + 1

    )

    return df



def missing_value_report(df):



    missing = df.isnull().sum()

    missing = missing[
        missing > 0
    ]

    if len(missing) == 0:

        print(
            "\nNo missing values found."
        )

    else:

        print(
            "\nMissing Values:"
        )

        print(missing)



def dataset_summary(df):


    print("\n================================")

    print("DATASET SUMMARY")

    print("================================")

    print(f"\nRows: {len(df)}")

    print(f"Columns: {len(df.columns)}")

    print("\nColumn List:")

    for col in df.columns:

        print(f" - {col}")

    timestamp_col = COLUMN_NAMES[
        "timestamp"
    ]

    if timestamp_col in df.columns:

        print(
            f"\nStart:\n"
            f"{df[timestamp_col].min()}"
        )

        print(
            f"\nEnd:\n"
            f"{df[timestamp_col].max()}"
        )



def basic_cleaning_pipeline(df):


    df = standardize_timestamp_column(df)

    df = remove_duplicate_timestamps(df)

    df = sort_by_timestamp(df)

    df = add_time_features(df)

    return df


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    try:

        df = load_dataset(
            "cleaned_demand"
        )

        dataset_summary(df)

        missing_value_report(df)

    except Exception as e:

        print(f"\nERROR:\n{e}")