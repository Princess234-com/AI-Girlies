import traceback
from datetime import datetime

from data.create_master_dataset import run_master_dataset_pipeline

from forecasting.feature_engineering import run_feature_engineering
from forecasting.grid_stress import run_grid_stress_pipeline
from forecasting.forecast_model import run_forecast_training_pipeline
from forecasting.future_forecast_generator import run_future_forecast_pipeline
from forecasting.pricing_model import run_pricing_pipeline
from forecasting.validate_data import run_validation_pipeline
from forecasting.live_data_updater import run_live_data_pipeline

from regional.regional_demand import run_regional_demand_pipeline
from regional.regional_pricing import run_regional_pricing_pipeline

from optimization.scheduler import run_scheduler
from optimization.recommendation_engine import run_recommendation_engine

from scheduler.top_time_selector import run_top_selector
from scheduler.automatic_mode import run_automatic_mode
from scheduler.manual_mode import run_manual_mode

from iot.device_simulator import display_all_devices
from iot.command_dispatcher import automatic_dispatch


PIPELINE_STEPS = [
    ("Master Dataset Pipeline", run_master_dataset_pipeline),
    ("Feature Engineering", run_feature_engineering),
    ("Grid Stress Engine", run_grid_stress_pipeline),
    ("Dataset Validation", run_validation_pipeline),
    ("Forecast Model Training", run_forecast_training_pipeline),
    ("Future Forecast Generation", run_future_forecast_pipeline),
    ("Pricing Engine", run_pricing_pipeline),
    ("Live Data Simulation", run_live_data_pipeline),
    ("Regional Demand Modelling", run_regional_demand_pipeline),
    ("Regional Pricing Modelling", run_regional_pricing_pipeline),
    ("Smart Scheduler", run_scheduler),
    ("Recommendation Engine", run_recommendation_engine),
    ("Top Schedule Selector", run_top_selector),
    ("Automatic Scheduling Mode", run_automatic_mode),
    ("Manual Scheduling Mode", run_manual_mode),
]


def display_header():
    
    print("GRIDFLEX AI")
    print("INTELLIGENT ENERGY OPTIMIZATION PLATFORM")
    print(f"\nPipeline Started: {datetime.now()}")


def display_footer(successful_steps, failed_steps):
    print("PIPELINE SUMMARY")

    print(f"\nSuccessful Steps: {len(successful_steps)}")
    for step in successful_steps:
        print(f"OK -> {step}")

    print(f"\nFailed Steps: {len(failed_steps)}")
    for step in failed_steps:
        print(f"FAIL -> {step}")

    print(f"\nPipeline Finished: {datetime.now()}")


def execute_step(step_name, step_function):
    print(f"RUNNING: {step_name}")

    try:
        step_function()
        print(f"\nSUCCESS: {step_name}")
        return True

    except Exception as error:
        print(f"\nFAILED: {step_name}")
        print("\nERROR:")
        print(error)
        print("\nTRACEBACK:")
        traceback.print_exc()
        return False


def run_gridflex_pipeline():
    display_header()

    successful_steps = []
    failed_steps = []

    for step_name, step_function in PIPELINE_STEPS:
        success = execute_step(step_name, step_function)

        if success:
            successful_steps.append(step_name)
        else:
            failed_steps.append(step_name)

    display_footer(successful_steps, failed_steps)

    return {
        "successful_steps": successful_steps,
        "failed_steps": failed_steps
    }


if __name__ == "__main__":
    run_gridflex_pipeline()