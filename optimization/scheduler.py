
import pandas as pd

from typing import Optional, List

from optimization.device_constraints import (
    DEVICE_CONSTRAINTS,
    is_valid_start_hour,
    is_preferred_hour,
    calculate_energy_usage
)

from optimization.optimization_engine import (
    calculate_final_score,
    interpret_score
)

from config import (
    PATHS,
    USER_SETTINGS
)

from regional.regional_config import (
    REGIONAL_CONFIG
)



def get_config_value(config, key, default=None):
  

    if isinstance(config, dict):
        return config.get(key, default)

    return getattr(config, key, default)




def load_scheduler_dataset():

    print("\nLoading scheduling dataset...")

    df = pd.read_csv(
        PATHS["pricing_dataset"]
    )

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"]
    )

    df["DATE"] = df["TIMESTAMP"].dt.date
    df["HOUR"] = df["TIMESTAMP"].dt.hour

    required_columns = [
        "TIMESTAMP",
        "GRID_STRESS_SCORE",
        "RENEWABLE_RATIO",
        "CARBON_INTENSITY",
        "NATIONAL_PRICE",
        "ND"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    return df



def apply_regional_pricing(
    df: pd.DataFrame,
    region: str
):

    if region not in REGIONAL_CONFIG:
        raise ValueError(
            f"Invalid region: {region}"
        )

    region_price_col = f"{region}_PRICE"

    if region_price_col in df.columns:
        df["ACTIVE_PRICE"] = df[region_price_col]
    else:
        df["ACTIVE_PRICE"] = df["NATIONAL_PRICE"]

    return df



def generate_possible_windows(
    df: pd.DataFrame,
    appliance_name: str
):

    appliance = DEVICE_CONSTRAINTS[
        appliance_name
    ]

    duration_periods = int(
        appliance.duration_hours * 2
    )

    windows = []

    for i in range(
        len(df) - duration_periods
    ):

        window = df.iloc[
            i:i + duration_periods
        ].copy()

        windows.append(window)

    return windows




def validate_window(
    window: pd.DataFrame,
    appliance_name: str,
    allowed_hours: Optional[List[int]] = None
):

    start_hour = window.iloc[0]["HOUR"]

    if not is_valid_start_hour(
        appliance_name,
        start_hour
    ):
        return False

    if allowed_hours:
        if start_hour not in allowed_hours:
            return False

    return True



def extract_window_features(
    window: pd.DataFrame
):



    demand_column = (
        "PREDICTED_DEMAND"
        if "PREDICTED_DEMAND" in window.columns
        else "ND"
    )

    features = {
        "average_price":
        window["ACTIVE_PRICE"].mean(),

        "average_grid_stress":
        window["GRID_STRESS_SCORE"].mean(),

        "renewable_ratio":
        window["RENEWABLE_RATIO"].mean(),

        "carbon_intensity":
        window["CARBON_INTENSITY"].mean(),

        "peak_demand":
        window[demand_column].max(),

        "average_demand":
        window[demand_column].mean()
    }

    return features




def optimize_appliance_schedule(
    df: pd.DataFrame,
    appliance_name: str,
    region: str,
    allowed_hours=None
):

    print(
        f"\nOptimizing {appliance_name}"
    )

    windows = generate_possible_windows(
        df,
        appliance_name
    )

    recommendations = []

    region_config = REGIONAL_CONFIG[
        region
    ]

    congestion_factor = get_config_value(
        region_config,
        "congestion_factor",
        1.0
    )

    volatility_factor = get_config_value(
        region_config,
        "volatility",
        0.05
    )

    for window in windows:

        if not validate_window(
            window,
            appliance_name,
            allowed_hours
        ):
            continue

        start_time = window.iloc[0]["TIMESTAMP"]
        end_time = window.iloc[-1]["TIMESTAMP"]
        start_hour = start_time.hour

        features = extract_window_features(
            window
        )

        score_breakdown = calculate_final_score(
            appliance_name=appliance_name,
            average_price=features["average_price"],
            average_grid_stress=features["average_grid_stress"],
            renewable_ratio=features["renewable_ratio"],
            carbon_intensity=features["carbon_intensity"],
            start_hour=start_hour,
            congestion_factor=congestion_factor,
            volatility_factor=volatility_factor
        )

        final_score = score_breakdown[
            "final_score"
        ]

        preferred_bonus = 0

        if is_preferred_hour(
            appliance_name,
            start_hour
        ):
            preferred_bonus = -0.05
            final_score += preferred_bonus

        estimated_savings = (
            df["ACTIVE_PRICE"].max()
            -
            features["average_price"]
        )

        energy_usage = calculate_energy_usage(
            appliance_name
        )

        recommendations.append({
            "region": region,
            "appliance": appliance_name,
            "start_time": start_time,
            "end_time": end_time,
            "start_hour": start_hour,
            "energy_kwh": energy_usage,

            "average_price": round(
                features["average_price"],
                2
            ),

            "average_grid_stress": round(
                features["average_grid_stress"],
                4
            ),

            "renewable_ratio": round(
                features["renewable_ratio"],
                4
            ),

            "carbon_intensity": round(
                features["carbon_intensity"],
                2
            ),

            "peak_demand": round(
                features["peak_demand"],
                2
            ),

            "average_demand": round(
                features["average_demand"],
                2
            ),

            "estimated_savings": round(
                estimated_savings,
                2
            ),

            "combined_score": round(
                final_score,
                4
            ),

            "schedule_quality": interpret_score(
                final_score
            ),

            **score_breakdown
        })

    result_df = pd.DataFrame(
        recommendations
    )

    if result_df.empty:
        return pd.DataFrame()

    result_df = (
        result_df
        .sort_values("combined_score")
        .head(
            USER_SETTINGS[
                "top_k_recommendations"
            ]
        )
        .reset_index(drop=True)
    )

    result_df["rank"] = result_df.index + 1

    return result_df



def generate_all_schedules(
    region="Midlands",
    allowed_hours=None
):

    df = load_scheduler_dataset()

    df = apply_regional_pricing(
        df,
        region
    )

    all_results = []

    for appliance_name in DEVICE_CONSTRAINTS.keys():

        appliance_df = optimize_appliance_schedule(
            df,
            appliance_name,
            region,
            allowed_hours
        )

        if not appliance_df.empty:
            all_results.append(
                appliance_df
            )

    if not all_results:
        raise ValueError(
            "No schedules generated."
        )

    final_df = pd.concat(
        all_results,
        ignore_index=True
    )

    return final_df



def save_results(
    schedule_df: pd.DataFrame
):

    output_path = PATHS[
        "optimized_schedule"
    ]

    schedule_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nSchedules saved:\n"
        f"{output_path}"
    )



def display_results(
    schedule_df: pd.DataFrame
):


    print("GRIDFLEX AI SCHEDULES")
    

    for appliance in schedule_df["appliance"].unique():

        print(f"\n{appliance}")

        appliance_df = schedule_df[
            schedule_df["appliance"] == appliance
        ]

        for row in appliance_df.itertuples():

            print(f"\nRank {row.rank}")
            print(f"Start: {row.start_time}")
            print(f"End: {row.end_time}")
            print(f"Score: {row.combined_score}")
            print(f"Quality: {row.schedule_quality}")
            print(
                f"Estimated Savings: "
                f"£{row.estimated_savings}"
            )



def run_scheduler(
    region="Midlands",
    allowed_hours=None
):

    
    print("GRIDFLEX AI SCHEDULER")
    

    schedule_df = generate_all_schedules(
        region=region,
        allowed_hours=allowed_hours
    )

    display_results(
        schedule_df
    )

    save_results(
        schedule_df
    )

    print("\nScheduling complete.")

    return schedule_df


#run

if __name__ == "__main__":

    run_scheduler(
        region="London"
    )

