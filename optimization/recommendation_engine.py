import pandas as pd

from config import PATHS



def load_schedule_data():


    print(
        "\nLoading optimized schedules..."
    )

    df = pd.read_csv(
        PATHS["optimized_schedule"]
    )

    df["start_time"] = pd.to_datetime(
        df["start_time"]
    )

    df["end_time"] = pd.to_datetime(
        df["end_time"]
    )

    return df



def generate_reason(row):

    reasons = []


    if row["average_price"] < 60:

        reasons.append(
            "very low electricity price"
        )

    elif row["average_price"] < 90:

        reasons.append(
            "moderate electricity price"
        )



    if row["average_grid_stress"] < 0.35:

        reasons.append(
            "low national grid stress"
        )

    elif row["average_grid_stress"] < 0.60:

        reasons.append(
            "moderate grid stress"
        )



    if row["renewable_ratio"] > 0.65:

        reasons.append(
            "high renewable generation"
        )


    if row["carbon_intensity"] < 150:

        reasons.append(
            "lower carbon intensity"
        )



    if row["discomfort_penalty"] < 0.25:

        reasons.append(
            "minimal user disruption"
        )



    reasons.append(
        f"{row['schedule_quality']} optimization score"
    )

    return ", ".join(reasons)



def assign_recommendation_label(
    rank
):


    labels = {

        1:
        "Best Option",

        2:
        "Recommended Alternative",

        3:
        "Flexible Alternative"
    }

    return labels.get(
        rank,
        "Alternative"
    )



def calculate_user_flexibility(
    row
):


    flexibility = 100

    flexibility -= (
        row["discomfort_penalty"] * 30
    )

    flexibility += (
        row["renewable_bonus"] * 20
    )

    flexibility -= (
        row["regional_penalty"] * 10
    )

    return max(
        round(flexibility, 1),
        0
    )




def generate_recommendations(
    df
):



    print(
        "\nGenerating recommendations..."
    )

    recommendations = []

    appliances = df[
        "appliance"
    ].unique()

    for appliance in appliances:

        appliance_df = (

            df[
                df["appliance"]
                == appliance
            ]

            .sort_values(
                "combined_score"
            )

            .reset_index(drop=True)
        )

        for rank, row in enumerate(

            appliance_df.itertuples(),

            start=1
        ):

            row_dict = row._asdict()

            recommendation = {

           

                "region":
                row_dict.get("region", "National"),

                "appliance":
                row.appliance,

                "rank":
                rank,

                "label":
                assign_recommendation_label(
                    rank
                ),

           #timing
                "start_time":
                row.start_time,

                "end_time":
                row.end_time,

                "start_hour":
                row.start_hour,

          #scores
                "combined_score":
                row.combined_score,

                "schedule_quality":
                row.schedule_quality,

                "average_price":
                row.average_price,

                "estimated_savings":
                row.estimated_savings,

                "renewable_ratio":
                row.renewable_ratio,

                "carbon_intensity":
                row.carbon_intensity,

                "grid_stress":
                row.average_grid_stress,
            #user experience

                "reason":
                generate_reason(
                    row_dict
                ),

                "user_flexibility_score":
                calculate_user_flexibility(
                    row_dict
                ),
            #modes

                "manual_mode":
                True,

                "automatic_mode":
                True,

                

                "schedule_status":
                "Pending",

                "command_sent":
                False,

                "execution_confirmed":
                False
            }

            recommendations.append(
                recommendation
            )

    recommendation_df = pd.DataFrame(
        recommendations
    )

    return recommendation_df



def display_recommendations(
    df
):
  

    print("GRIDFLEX AI RECOMMENDATIONS")


    appliances = (
        df["appliance"]
        .unique()
    )

    for appliance in appliances:

        print(f"\n{appliance}")

        appliance_df = df[
            df["appliance"]
            == appliance
        ]

        for row in appliance_df.itertuples():

            print(
                f"\nRank {row.rank}"
            )

            print(
                f"Label: {row.label}"
            )

            print(
                f"Start: {row.start_time}"
            )

            print(
                f"End: {row.end_time}"
            )

            print(
                f"Score: "
                f"{row.combined_score}"
            )

            print(
                f"Savings: "
                f"£{row.estimated_savings}"
            )

            print(
                f"Reason: {row.reason}"
            )

            print(
                f"Flexibility: "
                f"{row.user_flexibility_score}"
            )




def save_recommendations(
    df
):


    output_path = (
        PATHS[
            "schedule_recommendations"
        ]
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nRecommendations saved:\n"
        f"{output_path}"
    )




def simulate_user_selection(

    recommendation_df,

    appliance_name,

    selected_rank,

    mode="manual"
):
  

    selected = recommendation_df[

        (
            recommendation_df[
                "appliance"
            ]
            == appliance_name
        )

        &

        (
            recommendation_df[
                "rank"
            ]
            == selected_rank
        )
    ]

    if selected.empty:

        print(
            "No recommendation found."
        )

        return

    row = selected.iloc[0]


    print("GRIDFLEX AI CONFIRMATION")


    print(
        f"Appliance: "
        f"{row['appliance']}"
    )

    print(
        f"Selected Rank: "
        f"{row['rank']}"
    )

    print(
        f"Mode: "
        f"{mode.upper()}"
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
        f"Estimated Savings: "
        f"£{row['estimated_savings']}"
    )

    print(
        "\nSmart system "
        "has received the command."
    )

    if mode == "automatic":

        print(
            "Automatic execution enabled."
        )

    else:

        print(
            "Awaiting user confirmation."
        )




def run_recommendation_engine():
   


    print("GRIDFLEX AI RECOMMENDATION ENGINE")



    schedule_df = load_schedule_data()



    recommendation_df = (
        generate_recommendations(
            schedule_df
        )
    )


    display_recommendations(
        recommendation_df
    )


    save_recommendations(
        recommendation_df
    )

    print(
        "\nRecommendation engine complete."
    )

    return recommendation_df


if __name__ == "__main__":

    recommendations = (
        run_recommendation_engine()
    )

    # Example simulation

    simulate_user_selection(

        recommendations,

        appliance_name=
        "EV Charger",

        selected_rank=1,

        mode="automatic"
    )