import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smart Home Energy Optimiser", layout="wide")

st.title("AI Smart Home Energy Management System")
st.write("This prototype simulates electricity prices and recommends cheaper times to run flexible appliances.")

# -----------------------------
# Helper functions
# -----------------------------

def min_max_normalise(series):
    return (series - series.min()) / (series.max() - series.min())

def calculate_prices(df):
    df = df.copy()

    df["renewables"] = (
        df["EMBEDDED_WIND_GENERATION"] +
        df["EMBEDDED_SOLAR_GENERATION"]
    )

    interconnector_cols = [
        "IFA_FLOW", "IFA2_FLOW", "BRITNED_FLOW",
        "MOYLE_FLOW", "EAST_WEST_FLOW", "NEMO_FLOW",
        "NSL_FLOW", "ELECLINK_FLOW", "VIKING_FLOW", "GREENLINK_FLOW"
    ]

    df["interconnector"] = df[interconnector_cols].sum(axis=1)

    df["demand_norm"] = min_max_normalise(df["ND"])
    df["renewables_norm"] = min_max_normalise(df["renewables"])
    df["interconnector_norm"] = min_max_normalise(df["interconnector"])

    BASE_PRICE = 50
    ALPHA = 40
    BETA = 30
    GAMMA = 20
    DELTA = 60

    stress = df["demand_norm"] - df["renewables_norm"]

    df["simulated_price"] = (
        BASE_PRICE
        + ALPHA * df["demand_norm"]
        - BETA * df["renewables_norm"]
        - GAMMA * df["interconnector_norm"]
        + DELTA * np.maximum(0, stress) ** 2
    )

    df["simulated_price"] = df["simulated_price"].clip(lower=0)

    df["hour"] = (df["SETTLEMENT_PERIOD"] - 1) / 2

    peak_mask = (
        ((df["hour"] >= 7) & (df["hour"] <= 10)) |
        ((df["hour"] >= 16) & (df["hour"] <= 20))
    )

    df.loc[peak_mask, "simulated_price"] += 10

    df["price_per_kwh"] = df["simulated_price"] / 1000

    return df

def recommend_appliance_slot(df, runtime_hours, energy_kwh):
    slots_needed = int(runtime_hours * 2)  # 2 settlement periods per hour

    results = []

    for i in range(0, len(df) - slots_needed + 1):
        window = df.iloc[i:i + slots_needed]
        avg_price = window["price_per_kwh"].mean()
        estimated_cost = avg_price * energy_kwh

        results.append({
            "start_date": window.iloc[0]["SETTLEMENT_DATE"],
            "start_period": int(window.iloc[0]["SETTLEMENT_PERIOD"]),
            "start_hour": window.iloc[0]["hour"],
            "end_period": int(window.iloc[-1]["SETTLEMENT_PERIOD"]),
            "average_price_per_kwh": avg_price,
            "estimated_cost": estimated_cost
        })

    results_df = pd.DataFrame(results)
    cheapest = results_df.sort_values("estimated_cost").iloc[0]

    return cheapest, results_df

# -----------------------------
# Data upload
# -----------------------------

uploaded_file = st.file_uploader("Upload your NESO CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    required_cols = [
        "SETTLEMENT_DATE", "SETTLEMENT_PERIOD", "ND",
        "EMBEDDED_WIND_GENERATION", "EMBEDDED_SOLAR_GENERATION",
        "IFA_FLOW", "IFA2_FLOW", "BRITNED_FLOW", "MOYLE_FLOW",
        "EAST_WEST_FLOW", "NEMO_FLOW", "NSL_FLOW",
        "ELECLINK_FLOW", "VIKING_FLOW", "GREENLINK_FLOW"
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing columns: {missing_cols}")
    else:
        df = calculate_prices(df)

        st.success("Dataset loaded and prices simulated successfully.")

        # -----------------------------
        # Dashboard metrics
        # -----------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Lowest simulated price", f"£{df['simulated_price'].min():.2f}/MWh")

        with col2:
            st.metric("Highest simulated price", f"£{df['simulated_price'].max():.2f}/MWh")

        with col3:
            avg_price = df["simulated_price"].mean()
            st.metric("Average simulated price", f"£{avg_price:.2f}/MWh")

        # -----------------------------
        # Charts
        # -----------------------------

        st.subheader("Electricity Demand and Simulated Price")

        chart_df = df[["ND", "renewables", "simulated_price"]].copy()
        st.line_chart(chart_df)

        st.subheader("Price Data Preview")
        st.dataframe(
            df[[
                "SETTLEMENT_DATE",
                "SETTLEMENT_PERIOD",
                "ND",
                "renewables",
                "interconnector",
                "simulated_price",
                "price_per_kwh"
            ]].head(20)
        )

        # -----------------------------
        # Appliance scheduler
        # -----------------------------

        st.subheader("Appliance Scheduling Recommendation")

        appliance = st.selectbox(
            "Choose an appliance",
            ["Washing Machine", "Dishwasher", "EV Charging", "Immersion Heater", "HVAC"]
        )

        default_settings = {
            "Washing Machine": {"runtime": 2.0, "energy": 1.0},
            "Dishwasher": {"runtime": 1.5, "energy": 1.2},
            "EV Charging": {"runtime": 4.0, "energy": 28.0},
            "Immersion Heater": {"runtime": 2.0, "energy": 6.0},
            "HVAC": {"runtime": 3.0, "energy": 4.5}
        }

        runtime_hours = st.number_input(
            "Runtime in hours",
            min_value=0.5,
            max_value=12.0,
            value=default_settings[appliance]["runtime"],
            step=0.5
        )

        energy_kwh = st.number_input(
            "Estimated energy use in kWh",
            min_value=0.1,
            max_value=100.0,
            value=default_settings[appliance]["energy"],
            step=0.1
        )

        cheapest, all_slots = recommend_appliance_slot(df, runtime_hours, energy_kwh)

        st.write("### Recommended cheapest slot")

        col4, col5, col6 = st.columns(3)

        with col4:
            st.metric("Start date", cheapest["start_date"])

        with col5:
            st.metric("Start period", int(cheapest["start_period"]))

        with col6:
            st.metric("Estimated cost", f"£{cheapest['estimated_cost']:.2f}")

        st.write("All candidate schedules:")
        st.dataframe(all_slots.sort_values("estimated_cost").head(10))

else:
    st.info("Upload your NESO CSV file to begin.")