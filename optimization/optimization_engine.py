"""
==========================================================
GRIDFLEX AI
optimization/optimization_engine.py
==========================================================

PURPOSE
-------
Core multi-objective optimization engine.

This module combines:

1. Electricity Cost
2. Grid Stress
3. Carbon Intensity
4. Renewable Availability
5. User Comfort
6. Device Flexibility
7. Regional Effects

The optimizer generates a weighted score
used by the scheduler to rank scheduling windows.

Lower score = better schedule.

==========================================================
"""

from typing import Dict

import numpy as np

from optimization.device_constraints import (
    calculate_flexibility_score,
    get_device_constraint
)

from config import (
    OPTIMIZATION_WEIGHTS,
    NORMALIZATION_LIMITS
)


# ==========================================================
# NORMALIZATION
# ==========================================================

def normalize(
    value: float,
    min_value: float,
    max_value: float
) -> float:
    """
    Min-max normalization.
    """

    if max_value == min_value:
        return 0.0

    normalized = (
        (value - min_value)
        /
        (max_value - min_value)
    )

    return np.clip(normalized, 0, 1)


# ==========================================================
# COST SCORE
# ==========================================================

def calculate_cost_score(
    average_price: float
) -> float:
    """
    Lower electricity price = lower score.
    """

    return normalize(
        average_price,
        NORMALIZATION_LIMITS["price_min"],
        NORMALIZATION_LIMITS["price_max"]
    )


# ==========================================================
# GRID STRESS SCORE
# ==========================================================

def calculate_grid_stress_score(
    average_grid_stress: float
) -> float:
    """
    Higher grid stress = worse score.
    """

    return normalize(
        average_grid_stress,
        NORMALIZATION_LIMITS["stress_min"],
        NORMALIZATION_LIMITS["stress_max"]
    )


# ==========================================================
# CARBON SCORE
# ==========================================================

def calculate_carbon_score(
    carbon_intensity: float
) -> float:
    """
    Higher carbon intensity = worse.
    """

    return normalize(
        carbon_intensity,
        NORMALIZATION_LIMITS["carbon_min"],
        NORMALIZATION_LIMITS["carbon_max"]
    )


# ==========================================================
# RENEWABLE SCORE
# ==========================================================

def calculate_renewable_score(
    renewable_ratio: float
) -> float:
    """
    Higher renewables = better.

    We invert because lower score is better.
    """

    renewable_score = 1 - renewable_ratio

    return np.clip(
        renewable_score,
        0,
        1
    )


# ==========================================================
# DISCOMFORT PENALTY
# ==========================================================

def calculate_discomfort_penalty(
    appliance_name: str,
    start_hour: int
) -> float:
    """
    Penalize schedules outside comfortable hours.
    """

    device = get_device_constraint(
        appliance_name
    )

    if device is None:
        return 0.5

    # ------------------------------------------------------
    # LOW PENALTY
    # ------------------------------------------------------

    if start_hour in device.preferred_hours:
        return 0.0

    # ------------------------------------------------------
    # COMFORT SENSITIVE DEVICES
    # ------------------------------------------------------

    if device.comfort_sensitive:

        # Distance from preferred midpoint
        preferred_midpoint = np.mean(
            device.preferred_hours
        )

        distance = abs(
            start_hour - preferred_midpoint
        )

        return normalize(
            distance,
            0,
            12
        )

    # ------------------------------------------------------
    # NORMAL DEVICES
    # ------------------------------------------------------

    return 0.2


# ==========================================================
# FLEXIBILITY BONUS
# ==========================================================

def calculate_flexibility_bonus(
    appliance_name: str
) -> float:
    """
    Flexible devices receive optimization bonus.
    """

    flexibility_score = (
        calculate_flexibility_score(
            appliance_name
        )
    )

    normalized_bonus = normalize(
        flexibility_score,
        0,
        10
    )

    return normalized_bonus


# ==========================================================
# RENEWABLE PREFERENCE BONUS
# ==========================================================

def calculate_renewable_preference_bonus(
    appliance_name: str,
    renewable_ratio: float
) -> float:
    """
    Devices preferring renewables
    get bonus during renewable peaks.
    """

    device = get_device_constraint(
        appliance_name
    )

    if device is None:
        return 0

    if not device.renewable_preference:
        return 0

    return renewable_ratio * 0.15


# ==========================================================
# REGION ADJUSTMENT
# ==========================================================

def calculate_region_adjustment(
    congestion_factor: float,
    volatility_factor: float
) -> float:
    """
    Regional congestion penalty.
    """

    regional_penalty = (
        congestion_factor * 0.1
        +
        volatility_factor * 0.05
    )

    return regional_penalty


# ==========================================================
# FINAL MULTI-OBJECTIVE SCORE
# ==========================================================

def calculate_final_score(

    appliance_name: str,

    average_price: float,

    average_grid_stress: float,

    renewable_ratio: float,

    carbon_intensity: float,

    start_hour: int,

    congestion_factor: float = 1.0,

    volatility_factor: float = 0.0

) -> Dict:
    """
    Main optimization function.
    """

    # ======================================================
    # INDIVIDUAL SCORES
    # ======================================================

    cost_score = calculate_cost_score(
        average_price
    )

    stress_score = (
        calculate_grid_stress_score(
            average_grid_stress
        )
    )

    carbon_score = calculate_carbon_score(
        carbon_intensity
    )

    renewable_score = (
        calculate_renewable_score(
            renewable_ratio
        )
    )

    discomfort_penalty = (
        calculate_discomfort_penalty(
            appliance_name,
            start_hour
        )
    )

    flexibility_bonus = (
        calculate_flexibility_bonus(
            appliance_name
        )
    )

    renewable_bonus = (
        calculate_renewable_preference_bonus(
            appliance_name,
            renewable_ratio
        )
    )

    region_penalty = (
        calculate_region_adjustment(
            congestion_factor,
            volatility_factor
        )
    )

    # ======================================================
    # WEIGHTED SCORE
    # ======================================================

    final_score = (

        OPTIMIZATION_WEIGHTS["cost_weight"]
        * cost_score

        +

        OPTIMIZATION_WEIGHTS["stress_weight"]
        * stress_score

        +

        OPTIMIZATION_WEIGHTS["carbon_weight"]
        * carbon_score

        +

        OPTIMIZATION_WEIGHTS["renewable_weight"]
        * renewable_score

        +

        OPTIMIZATION_WEIGHTS["discomfort_weight"]
        * discomfort_penalty

        +

        region_penalty

        -

        flexibility_bonus * 0.08

        -

        renewable_bonus

    )

    final_score = max(final_score, 0)

    # ======================================================
    # RETURN BREAKDOWN
    # ======================================================

    return {

        "final_score":
        round(final_score, 4),

        "cost_score":
        round(cost_score, 4),

        "stress_score":
        round(stress_score, 4),

        "carbon_score":
        round(carbon_score, 4),

        "renewable_score":
        round(renewable_score, 4),

        "discomfort_penalty":
        round(discomfort_penalty, 4),

        "flexibility_bonus":
        round(flexibility_bonus, 4),

        "renewable_bonus":
        round(renewable_bonus, 4),

        "regional_penalty":
        round(region_penalty, 4)
    }


# ==========================================================
# SCORE INTERPRETATION
# ==========================================================

def interpret_score(
    score: float
) -> str:
    """
    Human-readable interpretation.
    """

    if score < 0.20:
        return "Excellent"

    if score < 0.35:
        return "Very Good"

    if score < 0.50:
        return "Good"

    if score < 0.70:
        return "Moderate"

    return "Poor"


# ==========================================================
# TESTING
# ==========================================================

if __name__ == "__main__":

    result = calculate_final_score(

        appliance_name="EV Charger",

        average_price=72,

        average_grid_stress=0.62,

        renewable_ratio=0.58,

        carbon_intensity=145,

        start_hour=1,

        congestion_factor=1.1,

        volatility_factor=0.04
    )

    print("\n===================================")
    print("GRIDFLEX AI OPTIMIZATION TEST")
    print("===================================")

    for key, value in result.items():

        print(f"{key}: {value}")

    print(
        "\nSchedule Quality:",
        interpret_score(
            result["final_score"]
        )
    )