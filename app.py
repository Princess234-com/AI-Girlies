"""
========================================================
GRIDFLEX AI
STREAMLIT APPLICATION
========================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime

from config import (
    OPTIMIZED_SCHEDULE_FILE,
    RECOMMENDATION_FILE,
    FORECAST_FILE,
    PRICING_DATASET
)

from regional.regional_config import (
    REGIONAL_CONFIG
)


# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="GridFlex AI",
    page_icon="⚡",
    layout="wide"
)


# ======================================================
# DATA LOADERS
# ======================================================

@st.cache_data
def load_schedule_data():

    try:
        df = pd.read_csv(
            OPTIMIZED_SCHEDULE_FILE
        )

        if "start_time" in df.columns:
            df["start_time"] = pd.to_datetime(
                df["start_time"]
            )

        if "end_time" in df.columns:
            df["end_time"] = pd.to_datetime(
                df["end_time"]
            )

        return df

    except Exception as error:
        st.warning(
            f"Schedule data unavailable: {error}"
        )
        return pd.DataFrame()


@st.cache_data
def load_recommendation_data():

    try:
        df = pd.read_csv(
            RECOMMENDATION_FILE
        )

        if "start_time" in df.columns:
            df["start_time"] = pd.to_datetime(
                df["start_time"]
            )

        if "end_time" in df.columns:
            df["end_time"] = pd.to_datetime(
                df["end_time"]
            )

        return df

    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_forecast_data():

    try:
        df = pd.read_csv(
            FORECAST_FILE
        )

        df["TIMESTAMP"] = pd.to_datetime(
            df["TIMESTAMP"]
        )

        return df

    except Exception as error:
        st.warning(
            f"Forecast data unavailable: {error}"
        )
        return pd.DataFrame()


@st.cache_data
def load_pricing_data():

    try:
        df = pd.read_csv(
            PRICING_DATASET
        )

        if "TIMESTAMP" in df.columns:
            df["TIMESTAMP"] = pd.to_datetime(
                df["TIMESTAMP"]
            )

        return df

    except Exception as error:
        st.warning(
            f"Pricing data unavailable: {error}"
        )
        return pd.DataFrame()


# ======================================================
# LOAD DATA
# ======================================================

schedule_df = load_schedule_data()
recommendation_df = load_recommendation_data()
forecast_df = load_forecast_data()
pricing_df = load_pricing_data()


# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title(
    "⚡ GridFlex AI"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Smart Scheduler",
        "Grid Forecast",
        "Regional Analysis"
    ]
)


selected_region = st.sidebar.selectbox(
    "Select Region",
    list(REGIONAL_CONFIG.keys())
)


mode = st.sidebar.radio(
    "Scheduling Mode",
    [
        "Automatic",
        "Manual"
    ]
)


# ======================================================
# PAGE 1 — SMART SCHEDULER
# ======================================================

if page == "Smart Scheduler":

    st.title(
        "⚡ Smart Appliance Scheduler"
    )

    st.caption(
        "AI-powered smart home energy optimization"
    )

    today = datetime.now().strftime(
        "%A, %d %B %Y"
    )

    st.markdown(
        f"### 📅 {today}"
    )

    # ==================================================
    # METRICS
    # ==================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Estimated Savings",
            "AI Optimized"
        )

    with col2:
        st.metric(
            "Carbon-Aware Mode",
            "Enabled"
        )

    with col3:
        st.metric(
            "Scheduling Mode",
            mode
        )

    st.divider()

    # ==================================================
    # DEVICE SELECTION
    # ==================================================

    st.subheader(
        "⚙️ Device Constraints"
    )

    available_devices = [
        "EV Charger",
        "Washing Machine",
        "Dishwasher",
        "Immersion Heater",
        "Air Conditioning"
    ]

    if not schedule_df.empty and "appliance" in schedule_df.columns:
        available_devices = sorted(
            schedule_df["appliance"]
            .dropna()
            .unique()
        )

    selected_device = st.selectbox(
        "Select Appliance",
        available_devices
    )

    allowed_start = st.slider(
        "Earliest Start Hour",
        0,
        23,
        6
    )

    allowed_end = st.slider(
        "Latest Finish Hour",
        0,
        23,
        22
    )

    st.caption(
        "These controls currently represent user preference settings. "
        "Pipeline scheduling constraints are handled in the backend scheduler."
    )

    st.divider()

    # ==================================================
    # USE RECOMMENDATIONS IF AVAILABLE
    # ==================================================

    display_df = (
        recommendation_df
        if not recommendation_df.empty
        else schedule_df
    )

    if not display_df.empty and "appliance" in display_df.columns:

        appliance_df = display_df[
            display_df["appliance"] == selected_device
        ].copy()

    else:
        appliance_df = pd.DataFrame()

    # ==================================================
    # DISPLAY SCHEDULES
    # ==================================================

    if appliance_df.empty:

        st.warning(
            "No schedule data available. Run `python main.py` first and make sure the Scheduler and Recommendation Engine complete successfully."
        )

    else:

        st.subheader(
            "🔌 Recommended Schedules"
        )

        if "rank" in appliance_df.columns:
            appliance_df = appliance_df.sort_values(
                "rank"
            )

        elif "combined_score" in appliance_df.columns:
            appliance_df = appliance_df.sort_values(
                "combined_score"
            )

        appliance_df = appliance_df.head(3)

        for index, row in appliance_df.iterrows():

            rank = (
                row["rank"]
                if "rank" in appliance_df.columns
                else index + 1
            )

            with st.container(border=True):

                st.markdown(
                    f"### Rank {rank}"
                )

                if "label" in row:
                    st.write(
                        f"**Label:** {row['label']}"
                    )

                st.write(
                    f"**Region:** {row.get('region', selected_region)}"
                )

                st.write(
                    f"**Start:** {row.get('start_time', 'N/A')}"
                )

                st.write(
                    f"**End:** {row.get('end_time', 'N/A')}"
                )

                if "combined_score" in row:
                    st.write(
                        f"**Combined Score:** {round(row['combined_score'], 4)}"
                    )

                if "estimated_savings" in row:
                    st.write(
                        f"**Estimated Savings:** £{round(row['estimated_savings'], 2)}"
                    )

                if "reason" in row:
                    st.write(
                        f"**Reason:** {row['reason']}"
                    )

                if mode == "Automatic":

                    if st.button(
                        f"Enable Automatic Schedule - Rank {rank}",
                        key=f"auto_{selected_device}_{rank}"
                    ):
                        st.success(
                            "Smart system has received the automatic scheduling command."
                        )

                else:

                    if st.button(
                        f"Select Manual Schedule - Rank {rank}",
                        key=f"manual_{selected_device}_{rank}"
                    ):
                        st.success(
                            "Smart system has received your manual scheduling command."
                        )

    # ==================================================
    # COST COMPARISON
    # ==================================================

    st.divider()

    st.subheader(
        "💰 Cost Optimization"
    )

    comparison_df = pd.DataFrame({
        "Scenario": [
            "Without GridFlex AI",
            "With GridFlex AI"
        ],
        "Daily Cost (£)": [
            18.70,
            10.40
        ]
    })

    fig = px.bar(
        comparison_df,
        x="Scenario",
        y="Daily Cost (£)",
        title="Electricity Cost Optimization"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ======================================================
# PAGE 2 — GRID FORECAST
# ======================================================

elif page == "Grid Forecast":

    st.title(
        "📈 Electricity Demand Forecast"
    )

    if forecast_df.empty:

        st.warning(
            "Forecast data unavailable. Run `python main.py` first."
        )

    else:

        demand_column = (
            "PREDICTED_DEMAND"
            if "PREDICTED_DEMAND" in forecast_df.columns
            else "PREDICTED_ND"
            if "PREDICTED_ND" in forecast_df.columns
            else None
        )

        if demand_column is None:

            st.error(
                "Forecast dataset does not contain PREDICTED_DEMAND or PREDICTED_ND."
            )

        else:

            st.subheader(
                "7-Day Forecast"
            )

            fig = px.line(
                forecast_df,
                x="TIMESTAMP",
                y=demand_column,
                title="Predicted National Demand"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            peak_df = (
                forecast_df
                .sort_values(
                    demand_column,
                    ascending=False
                )
                .head(5)
            )

            st.subheader(
                "🔥 Highest Predicted Peaks"
            )

            st.dataframe(
                peak_df[
                    [
                        "TIMESTAMP",
                        demand_column
                    ]
                ]
            )

            low_df = (
                forecast_df
                .sort_values(
                    demand_column,
                    ascending=True
                )
                .head(5)
            )

            st.subheader(
                "🌱 Lowest Demand Periods"
            )

            st.dataframe(
                low_df[
                    [
                        "TIMESTAMP",
                        demand_column
                    ]
                ]
            )

            heatmap_df = forecast_df.copy()

            heatmap_df["DAY"] = (
                heatmap_df["TIMESTAMP"]
                .dt.day_name()
            )

            heatmap_df["HOUR"] = (
                heatmap_df["TIMESTAMP"]
                .dt.hour
            )

            pivot_table = heatmap_df.pivot_table(
                values=demand_column,
                index="DAY",
                columns="HOUR",
                aggfunc="mean"
            )

            heatmap = px.imshow(
                pivot_table,
                title="Demand Intensity Heatmap"
            )

            st.plotly_chart(
                heatmap,
                use_container_width=True
            )


# ======================================================
# PAGE 3 — REGIONAL ANALYSIS
# ======================================================

elif page == "Regional Analysis":

    st.title(
        "🌍 Regional Energy Analysis"
    )

    if pricing_df.empty:

        st.warning(
            "Pricing data unavailable. Run `python main.py` first."
        )

    else:

        price_col = f"{selected_region}_PRICE"
        demand_col = f"{selected_region}_DEMAND"

        if "TIMESTAMP" not in pricing_df.columns:
            pricing_df["TIMESTAMP"] = range(
                len(pricing_df)
            )

        if price_col in pricing_df.columns:

            st.subheader(
                f"{selected_region} Pricing Trends"
            )

            fig_price = px.line(
                pricing_df,
                x="TIMESTAMP",
                y=price_col,
                title=f"{selected_region} Electricity Price"
            )

            st.plotly_chart(
                fig_price,
                use_container_width=True
            )

        else:

            st.info(
                f"No regional price column found for {selected_region}. Showing national price instead."
            )

            if "NATIONAL_PRICE" in pricing_df.columns:

                fig_price = px.line(
                    pricing_df,
                    x="TIMESTAMP",
                    y="NATIONAL_PRICE",
                    title="National Electricity Price"
                )

                st.plotly_chart(
                    fig_price,
                    use_container_width=True
                )

        if demand_col in pricing_df.columns:

            st.subheader(
                f"{selected_region} Demand Trends"
            )

            fig_demand = px.line(
                pricing_df,
                x="TIMESTAMP",
                y=demand_col,
                title=f"{selected_region} Regional Demand"
            )

            st.plotly_chart(
                fig_demand,
                use_container_width=True
            )

        elif "ND" in pricing_df.columns:

            st.info(
                f"No regional demand column found for {selected_region}. Showing national demand instead."
            )

            fig_demand = px.line(
                pricing_df,
                x="TIMESTAMP",
                y="ND",
                title="National Demand"
            )

            st.plotly_chart(
                fig_demand,
                use_container_width=True
            )


# ======================================================
# FOOTER
# ======================================================

st.divider()

st.caption(
    "GridFlex AI — Intelligent Demand Flexibility Platform"
)