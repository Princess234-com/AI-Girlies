# =========================================================
# FILE: forecasting/validate_data.py
# =========================================================

"""
GRIDFLEX AI — DATA VALIDATION ENGINE
---------------------------------------------------------

Purpose
-------
Validates all datasets before they enter:

- forecasting
- regional modelling
- optimization
- scheduling

This script prevents:

- missing critical columns
- invalid timestamps
- duplicate records
- impossible energy values
- broken pipelines
- NaN propagation

Academic Importance
-------------------
This improves:

- system robustness
- reproducibility
- data integrity
- engineering realism

Outputs
-------
Validation report in terminal.

Optionally:
------------
Raises errors if critical validation fails.

"""

# =========================================================
# IMPORTS
# =========================================================

import pandas as pd
import numpy as np

from pathlib import Path

from config import (
    PROCESSED_DATA_DIR
)

# =========================================================
# CONFIG
# =========================================================

VALIDATION_DATASETS = {

    "master_dataset": {
        "path": PROCESSED_DATA_DIR / "master_energy_dataset.csv",
        "required_columns": [
            "TIMESTAMP",
            "ND",
            "GRID_STRESS_SCORE",
            "RENEWABLE_RATIO"
        ]
    },

    "feature_store": {
        "path": PROCESSED_DATA_DIR / "feature_store.csv",
        "required_columns": [
            "TIMESTAMP",
            "ND",
            "HOUR",
            "DAY_OF_WEEK",
            "ND_LAG_1",
            "ND_ROLLING_24H"
        ]
    },

    "grid_stress_dataset": {
        "path": PROCESSED_DATA_DIR / "grid_stress_dataset.csv",
        "required_columns": [
            "TIMESTAMP",
            "ND",
            "GRID_STRESS_SCORE",
            "GRID_STATE",
            "RENEWABLE_RATIO"
        ]
    },

    "pricing_dataset": {
        "path": PROCESSED_DATA_DIR / "pricing_model_dataset.csv",
        "required_columns": [
            "TIMESTAMP",
            "ND",
            "NATIONAL_PRICE",
            "MARKET_STATE",
            "PRICE_CATEGORY"
        ]
    }
}

# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset(dataset_path):

    if not dataset_path.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{dataset_path}"
        )

    return pd.read_csv(dataset_path)

# =========================================================
# CHECK REQUIRED COLUMNS
# =========================================================

def validate_required_columns(

    df,
    required_columns

):

    missing = [

        col for col in required_columns
        if col not in df.columns

    ]

    return missing

# =========================================================
# CHECK NULL VALUES
# =========================================================

def validate_missing_values(df):

    null_counts = (
        df.isnull()
        .sum()
    )

    null_counts = (
        null_counts[
            null_counts > 0
        ]
    )

    return null_counts

# =========================================================
# CHECK DUPLICATES
# =========================================================

def validate_duplicates(df):

    duplicates = df.duplicated().sum()

    return duplicates

# =========================================================
# CHECK TIMESTAMP
# =========================================================

def validate_timestamp(df):

    if "TIMESTAMP" not in df.columns:

        return "TIMESTAMP column missing"

    try:

        timestamps = pd.to_datetime(
            df["TIMESTAMP"]
        )

    except Exception as error:

        return f"Timestamp conversion failed: {error}"

    if timestamps.isnull().sum() > 0:

        return (
            "Invalid timestamp values detected"
        )

    return None

# =========================================================
# CHECK NUMERIC RANGES
# =========================================================

def validate_numeric_ranges(df):

    issues = []

    numeric_checks = {

        "ND": (0, 100000),

        "GRID_STRESS_SCORE": (0, 1),

        "RENEWABLE_RATIO": (0, 1),

        "NATIONAL_PRICE": (0, 1000)

    }

    for column, (min_val, max_val) in (

        numeric_checks.items()

    ):

        if column not in df.columns:

            continue

        invalid = df[
            (
                df[column] < min_val
            )
            |
            (
                df[column] > max_val
            )
        ]

        if len(invalid) > 0:

            issues.append(

                f"{column}: "
                f"{len(invalid)} invalid values"

            )

    return issues

# =========================================================
# VALIDATE DATASET
# =========================================================

def validate_dataset(

    dataset_name,
    dataset_info

):

    print("\n===================================")
    print(f"VALIDATING: {dataset_name}")
    print("===================================")

    dataset_path = dataset_info["path"]

    required_columns = (
        dataset_info["required_columns"]
    )

    # =====================================================
    # LOAD
    # =====================================================

    try:

        df = load_dataset(dataset_path)

    except Exception as error:

        print(f"FAILED TO LOAD:\n{error}")

        return False

    print(
        f"Rows Loaded: {len(df):,}"
    )

    # =====================================================
    # REQUIRED COLUMNS
    # =====================================================

    missing_columns = validate_required_columns(

        df,
        required_columns

    )

    if missing_columns:

        print(
            f"\nMissing Columns:\n"
            f"{missing_columns}"
        )

    else:

        print(
            "Required Columns: OK"
        )

    # =====================================================
    # NULL VALUES
    # =====================================================

    null_values = validate_missing_values(df)

    if len(null_values) > 0:

        print("\nMissing Values:")

        print(null_values)

    else:

        print("Missing Values: OK")

    # =====================================================
    # DUPLICATES
    # =====================================================

    duplicates = validate_duplicates(df)

    if duplicates > 0:

        print(
            f"Duplicate Rows: {duplicates}"
        )

    else:

        print("Duplicate Rows: OK")

    # =====================================================
    # TIMESTAMP
    # =====================================================

    timestamp_issue = validate_timestamp(df)

    if timestamp_issue:

        print(
            f"Timestamp Issue:\n"
            f"{timestamp_issue}"
        )

    else:

        print("Timestamp Validation: OK")

    # =====================================================
    # NUMERIC VALIDATION
    # =====================================================

    numeric_issues = validate_numeric_ranges(df)

    if numeric_issues:

        print("\nNumeric Range Issues:")

        for issue in numeric_issues:

            print(f"- {issue}")

    else:

        print("Numeric Ranges: OK")

    # =====================================================
    # FINAL STATUS
    # =====================================================

    critical_failure = (

        len(missing_columns) > 0

        or

        timestamp_issue is not None

    )

    if critical_failure:

        print("\nVALIDATION STATUS: FAILED")

    else:

        print("\nVALIDATION STATUS: PASSED")

    return not critical_failure

# =========================================================
# RUN FULL VALIDATION
# =========================================================

def run_validation_pipeline():

    print("\n===================================")
    print("GRIDFLEX AI DATA VALIDATION")
    print("===================================")

    passed = []
    failed = []

    for dataset_name, dataset_info in (

        VALIDATION_DATASETS.items()

    ):

        success = validate_dataset(

            dataset_name,
            dataset_info

        )

        if success:

            passed.append(dataset_name)

        else:

            failed.append(dataset_name)

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print("\n===================================")
    print("VALIDATION SUMMARY")
    print("===================================")

    print(
        f"\nPassed: {len(passed)}"
    )

    for item in passed:

        print(f"OK -> {item}")

    print(
        f"\nFailed: {len(failed)}"
    )

    for item in failed:

        print(f"FAIL -> {item}")

    # =====================================================
    # PIPELINE STATUS
    # =====================================================

    if failed:

        raise ValueError(
            "\nValidation pipeline failed."
        )

    print("\nAll datasets validated successfully.")

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_validation_pipeline()