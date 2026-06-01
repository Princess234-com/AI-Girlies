import pandas as pd

from config import (
    OPTIMIZED_SCHEDULE_FILE,
    TOP_SCHEDULE_FILE,
    TOP_K_RECOMMENDATIONS
)



def load_schedule_data():

    print("\nLoading optimized schedules...")

    df = pd.read_csv(
        OPTIMIZED_SCHEDULE_FILE
    )

    if df.empty:

        raise ValueError(
            "Optimized schedule dataset is empty."
        )




    df["start_time"] = pd.to_datetime(
        df["start_time"]
    )

    df["end_time"] = pd.to_datetime(
        df["end_time"]
    )

    return df




def has_overlap(

    start_a,
    end_a,
    start_b,
    end_b

):

    return (

        start_a < end_b

        and

        end_a > start_b

    )




def remove_overlaps(df):

    print(
        "\nRemoving overlapping schedules..."
    )

    final_results = []

    appliances = sorted(
        df["appliance"].unique()
    )

    for appliance in appliances:

        appliance_df = df[

            df["appliance"]
            == appliance

        ].copy()



        appliance_df = appliance_df.sort_values(
            "combined_score"
        )

        selected_windows = []

        for _, row in appliance_df.iterrows():

            overlap_found = False

            for selected in selected_windows:

                if has_overlap(

                    row["start_time"],
                    row["end_time"],

                    selected["start_time"],
                    selected["end_time"]

                ):

                    overlap_found = True
                    break



            if not overlap_found:

                selected_windows.append(row)



            if len(selected_windows) >= TOP_K_RECOMMENDATIONS:

                break



        for rank, schedule in enumerate(

            selected_windows,
            start=1

        ):

            schedule_dict = schedule.to_dict()

            schedule_dict["rank"] = rank

            final_results.append(
                schedule_dict
            )

    final_df = pd.DataFrame(
        final_results
    )

    return final_df




def display_top_schedules(df):



    print(
        "GRIDFLEX AI TOP SCHEDULES"
    )



    appliances = sorted(
        df["appliance"].unique()
    )

    for appliance in appliances:

        print(f"\n{appliance}")

        appliance_df = df[

            df["appliance"]
            == appliance

        ]

        for _, row in appliance_df.iterrows():

            print(
                f"\nRank {row['rank']}"
            )

            print(
                f"Start: {row['start_time']}"
            )

            print(
                f"End: {row['end_time']}"
            )

            print(
                f"Combined Score: "
                f"{round(row['combined_score'], 4)}"
            )

            print(
                f"Estimated Savings: £"
                f"{round(row['estimated_savings'], 2)}"
            )



def save_results(df):

    df.to_csv(
        TOP_SCHEDULE_FILE,
        index=False
    )

    print(
        f"\nSaved top schedules:\n"
        f"{TOP_SCHEDULE_FILE}"
    )



def run_top_time_selector():



    print(
        "GRIDFLEX AI TOP TIME SELECTOR"
    )

 



    df = load_schedule_data()

   

    final_df = remove_overlaps(df)


    display_top_schedules(
        final_df
    )



    save_results(
        final_df
    )

    print(
        "\nTop time selection complete."
    )

    return final_df



if __name__ == "__main__":

    run_top_time_selector()