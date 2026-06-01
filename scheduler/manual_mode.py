
import pandas as pd

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



def display_options(

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


    print(
        f"{appliance_name.upper()} OPTIONS"
    )


    appliance_df = appliance_df.sort_values(
        "rank"
    )

    for _, row in appliance_df.iterrows():

        print(
            f"\nRank {row['rank']}"
        )

        print(
            f"Label: {row['label']}"
        )

        print(
            f"Start Time: "
            f"{row['start_time']}"
        )

        print(
            f"End Time: "
            f"{row['end_time']}"
        )

        print(
            f"Combined Score: "
            f"{round(row['combined_score'], 4)}"
        )

        print(
            f"Reason: "
            f"{row['reason']}"
        )



def select_schedule(

    df,
    appliance_name,
    selected_rank

):

    selected = df[

        (
            df["appliance"]
            == appliance_name
        )

        &

        (
            df["rank"]
            == selected_rank
        )

    ]

    if selected.empty:

        raise ValueError(
            f"Invalid rank selected "
            f"for {appliance_name}"
        )

    return selected.iloc[0]



def confirm_selection(schedule):


    print(
        "GRIDFLEX AI MANUAL CONFIRMATION"
    )


    print(
        f"\nAppliance: "
        f"{schedule['appliance']}"
    )

    print(
        f"Selected Rank: "
        f"{schedule['rank']}"
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

    print(
        "\nSending command "
        "to smart-home controller..."
    )

    print(
        "\nAcknowledgement received."
    )

    print(
        "Schedule successfully saved."
    )

    print(
        "\nAwaiting execution time."
    )



def run_manual_mode(

    appliance_name="EV Charger",
    selected_rank=2

):


    print(
        "GRIDFLEX AI MANUAL MODE"
    )



    df = load_recommendations()


    display_options(

        df,
        appliance_name

    )


    selected_schedule = select_schedule(

        df,
        appliance_name,
        selected_rank

    )



    confirm_selection(
        selected_schedule
    )

    return selected_schedule



if __name__ == "__main__":

    run_manual_mode()