"""
========================================================
GRIDFLEX AI
DAILY AUTOMATION PIPELINE
========================================================

Purpose:
Runs the full GridFlex AI pipeline:

1. Forecast demand
2. Generate pricing
3. Run optimization
4. Generate schedules
5. Generate recommendations

This simulates:
- continual learning
- rolling forecasting
- adaptive smart-grid intelligence

========================================================
"""

import subprocess
import sys
import time

from datetime import datetime


# ======================================================
# PIPELINE STEPS
# ======================================================

PIPELINE_STEPS = [

    {
        "name":
        "Future Demand Forecasting",

        "module":
        "forecasting.future_forecast_generator"
    },

    {
        "name":
        "Regional Demand Generation",

        "module":
        "regional.regional_demand"
    },

    {
        "name":
        "Regional Pricing Generation",

        "module":
        "regional.regional_pricing"
    },

    {
        "name":
        "Optimization Scheduler",

        "module":
        "optimization.scheduler"
    },

    {
        "name":
        "Top Time Selector",

        "module":
        "scheduler.top_time_selector"
    },

    {
        "name":
        "Recommendation Engine",

        "module":
        "optimization.recommendation_engine"
    }

]


# ======================================================
# BANNERS
# ======================================================

def print_banner():

    print(
        "\n=================================================="
    )

    print(
        "GRIDFLEX AI DAILY PIPELINE"
    )

    print(
        "=================================================="
    )

    print(
        f"Started: {datetime.now()}"
    )


def print_step(name):

    print(
        "\n--------------------------------------------------"
    )

    print(
        f"RUNNING: {name}"
    )

    print(
        "--------------------------------------------------"
    )


# ======================================================
# RUN MODULE
# ======================================================

def run_module(module_name):

    start = time.time()

    command = [

        sys.executable,
        "-m",
        module_name

    ]

    result = subprocess.run(

        command,

        capture_output=True,

        text=True

    )

    runtime = round(

        time.time() - start,
        2

    )

    return result, runtime


# ======================================================
# EXECUTE PIPELINE
# ======================================================

def run_pipeline():

    print_banner()

    successful_steps = []

    failed_steps = []

    total_start = time.time()

    # ==================================================
    # RUN EACH STEP
    # ==================================================

    for step in PIPELINE_STEPS:

        step_name = step["name"]

        module_name = step["module"]

        print_step(step_name)

        result, runtime = run_module(
            module_name
        )

        # ==============================================
        # SUCCESS
        # ==============================================

        if result.returncode == 0:

            print(
                f"SUCCESS "
                f"({runtime}s)"
            )

            print(result.stdout)

            successful_steps.append({

                "step": step_name,

                "runtime": runtime

            })

        # ==============================================
        # FAILURE
        # ==============================================

        else:

            print(
                f"FAILED "
                f"({runtime}s)"
            )

            print(result.stderr)

            failed_steps.append({

                "step": step_name,

                "runtime": runtime,

                "error": result.stderr

            })

    # ==================================================
    # FINAL SUMMARY
    # ==================================================

    total_runtime = round(

        time.time() - total_start,
        2

    )

    print(
        "\n=================================================="
    )

    print(
        "PIPELINE SUMMARY"
    )

    print(
        "=================================================="
    )

    print(
        f"\nSuccessful Steps: "
        f"{len(successful_steps)}"
    )

    for item in successful_steps:

        print(
            f"OK -> "
            f"{item['step']} "
            f"({item['runtime']}s)"
        )

    print(
        f"\nFailed Steps: "
        f"{len(failed_steps)}"
    )

    for item in failed_steps:

        print(
            f"FAIL -> "
            f"{item['step']} "
            f"({item['runtime']}s)"
        )

    print(
        f"\nTotal Runtime: "
        f"{total_runtime}s"
    )

    print(
        f"\nFinished: "
        f"{datetime.now()}"
    )

    # ==================================================
    # FINAL STATUS
    # ==================================================

    if len(failed_steps) == 0:

        print(
            "\nGRIDFLEX AI "
            "pipeline completed successfully."
        )

    else:

        print(
            "\nPipeline completed "
            "with errors."
        )


# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":

    run_pipeline()