import pandas as pd
from datetime import datetime

from config import (
    RECOMMENDATION_FILE
)


def load_recommendations():

    print(
        "\nLoading recommendations..."
    )

    df = pd.read_csv(
        RECOMMENDATION_FILE
    )

    if df.empty:

        raise ValueError(
            "Recommendation dataset is empty."
        )


    df["start_time"] = pd.to_datetime(
        df["start_time"]
    )

    df["end_time"] = pd.to_datetime(
        df["end_time"]
    )

    return df


def select_best_schedule(

    df,
    appliance_name

):

    appliance_df = df[

        df["appliance"]
        == appliance_name

    ].copy()

    if appliance_df.empty:

        raise ValueError(
            f"No schedules found for "
            f"{appliance_name}"
        )


    appliance_df = appliance_df.sort_values(
        "combined_score"
    )

    best_schedule = appliance_df.iloc[0]

    return best_schedule


def send_device_command(

    appliance_name,
    start_time,
    end_time

):

    print(
        "\nSending smart-home command..."
    )

    command_payload = {

        "device": appliance_name,

        "start_time": str(start_time),

        "end_time": str(end_time),

        "command": "START_DEVICE"

    }

    print(
        f"\nPayload:\n{command_payload}"
    )


    acknowledgement = {

        "status": "SUCCESS",

        "message":
        "Device acknowledged command."

    }

    return acknowledgement

def execute_schedule(schedule):



    print(
        "GRIDFLEX AI AUTO EXECUTION"
    )



    print(
        f"\nAppliance: "
        f"{schedule['appliance']}"
    )

    print(
        f"Start Time: "
        f"{schedule['start_time']}"
    )

    print(
        f"End Time: "
        f"{schedule['end_time']}"
    )

    print(
        f"Optimization Score: "
        f"{round(schedule['combined_score'], 4)}"
    )


    response = send_device_command(

        appliance_name=
        schedule["appliance"],

        start_time=
        schedule["start_time"],

        end_time=
        schedule["end_time"]

    )

    print(
        "\nDevice Response:"
    )

    print(
        f"Status: "
        f"{response['status']}"
    )

    print(
        f"Message: "
        f"{response['message']}"
    )

    print(
        "\nAutomatic scheduling complete."
    )


def run_automatic_mode(

    appliance_name="EV Charger"

):



    print(
        "GRIDFLEX AI AUTOMATIC MODE"
    )

  

    df = load_recommendations()

    best_schedule = select_best_schedule(

        df,
        appliance_name

    )


    execute_schedule(
        best_schedule
    )

    return best_schedule

if __name__ == "__main__":

    run_automatic_mode()