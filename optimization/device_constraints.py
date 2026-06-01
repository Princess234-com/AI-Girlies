"""
==========================================================
GRIDFLEX AI
optimization/device_constraints.py
==========================================================

PURPOSE
-------
Centralized appliance/device constraint management system.

This module defines:
- smart appliance operational constraints
- user comfort boundaries
- scheduling flexibility
- energy usage behaviour
- optimization metadata

Used by:
- scheduler engine
- optimization engine
- recommendation engine
- Streamlit UI
- future IoT integration

==========================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ==========================================================
# DEVICE CONSTRAINT MODEL
# ==========================================================

@dataclass
class DeviceConstraint:
    """
    Smart appliance constraint definition.
    """

    # ------------------------------------------------------
    # BASIC INFO
    # ------------------------------------------------------

    name: str

    category: str

    # ------------------------------------------------------
    # ENERGY CHARACTERISTICS
    # ------------------------------------------------------

    power_kw: float

    duration_hours: float

    standby_power_kw: float = 0.0

    # ------------------------------------------------------
    # USER TIME CONSTRAINTS
    # ------------------------------------------------------

    earliest_start_hour: int = 0

    latest_finish_hour: int = 23

    preferred_hours: List[int] = field(default_factory=list)

    restricted_hours: List[int] = field(default_factory=list)

    # ------------------------------------------------------
    # EXECUTION RULES
    # ------------------------------------------------------

    interruptible: bool = False

    max_daily_runs: int = 1

    minimum_runtime_hours: float = 1.0

    # ------------------------------------------------------
    # OPTIMIZATION PRIORITIES
    # ------------------------------------------------------

    priority: int = 3
    """
    1 = Critical
    2 = Important
    3 = Flexible
    """

    comfort_sensitive: bool = False

    carbon_sensitive: bool = False

    renewable_preference: bool = False

    # ------------------------------------------------------
    # EV / BATTERY SUPPORT
    # ------------------------------------------------------

    battery_dependent: bool = False

    preferred_soc_target: Optional[int] = None

    # ------------------------------------------------------
    # USER EXPERIENCE
    # ------------------------------------------------------

    user_override_allowed: bool = True

    automation_enabled: bool = True

    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    def validate(self):

        if self.power_kw <= 0:
            raise ValueError(
                f"{self.name}: power_kw must be > 0"
            )

        if self.duration_hours <= 0:
            raise ValueError(
                f"{self.name}: duration_hours must be > 0"
            )

        if not (0 <= self.earliest_start_hour <= 23):
            raise ValueError(
                f"{self.name}: invalid earliest_start_hour"
            )

        if not (0 <= self.latest_finish_hour <= 23):
            raise ValueError(
                f"{self.name}: invalid latest_finish_hour"
            )


# ==========================================================
# CENTRAL DEVICE LIBRARY
# ==========================================================

DEVICE_CONSTRAINTS: Dict[str, DeviceConstraint] = {

    # ======================================================
    # EV CHARGER
    # ======================================================

    "EV Charger": DeviceConstraint(

        name="EV Charger",

        category="Transport",

        power_kw=7.2,

        duration_hours=4,

        standby_power_kw=0.05,

        earliest_start_hour=22,

        latest_finish_hour=7,

        preferred_hours=[
            22, 23, 0, 1, 2, 3
        ],

        restricted_hours=[
            16, 17, 18, 19
        ],

        interruptible=False,

        max_daily_runs=1,

        minimum_runtime_hours=2,

        priority=1,

        comfort_sensitive=False,

        carbon_sensitive=True,

        renewable_preference=True,

        battery_dependent=True,

        preferred_soc_target=80,

        automation_enabled=True
    ),

    # ======================================================
    # WASHING MACHINE
    # ======================================================

    "Washing Machine": DeviceConstraint(

        name="Washing Machine",

        category="Appliance",

        power_kw=1.2,

        duration_hours=2,

        standby_power_kw=0.01,

        earliest_start_hour=7,

        latest_finish_hour=21,

        preferred_hours=[
            9, 10, 11, 12, 13, 14
        ],

        restricted_hours=[
            22, 23, 0, 1, 2, 3, 4, 5
        ],

        interruptible=False,

        max_daily_runs=2,

        minimum_runtime_hours=1.5,

        priority=2,

        comfort_sensitive=False,

        carbon_sensitive=False,

        renewable_preference=True
    ),

    # ======================================================
    # DISHWASHER
    # ======================================================

    "Dishwasher": DeviceConstraint(

        name="Dishwasher",

        category="Appliance",

        power_kw=1.5,

        duration_hours=2,

        standby_power_kw=0.02,

        earliest_start_hour=18,

        latest_finish_hour=23,

        preferred_hours=[
            19, 20, 21
        ],

        restricted_hours=[
            0, 1, 2, 3, 4, 5
        ],

        interruptible=False,

        max_daily_runs=1,

        minimum_runtime_hours=1.5,

        priority=2,

        comfort_sensitive=False,

        carbon_sensitive=False,

        renewable_preference=True
    ),

    # ======================================================
    # IMMERSION HEATER
    # ======================================================

    "Immersion Heater": DeviceConstraint(

        name="Immersion Heater",

        category="Heating",

        power_kw=3.0,

        duration_hours=3,

        standby_power_kw=0.05,

        earliest_start_hour=0,

        latest_finish_hour=6,

        preferred_hours=[
            1, 2, 3, 4
        ],

        interruptible=True,

        max_daily_runs=2,

        minimum_runtime_hours=1,

        priority=1,

        comfort_sensitive=False,

        carbon_sensitive=True,

        renewable_preference=True
    ),

    # ======================================================
    # AIR CONDITIONING
    # ======================================================

    "Air Conditioning": DeviceConstraint(

        name="Air Conditioning",

        category="Climate",

        power_kw=2.5,

        duration_hours=3,

        standby_power_kw=0.15,

        earliest_start_hour=10,

        latest_finish_hour=22,

        preferred_hours=[
            12, 13, 14, 15, 16, 17
        ],

        interruptible=True,

        max_daily_runs=3,

        minimum_runtime_hours=1,

        priority=3,

        comfort_sensitive=True,

        carbon_sensitive=False,

        renewable_preference=False
    )
}


# ==========================================================
# VALIDATE ALL DEVICES
# ==========================================================

for device in DEVICE_CONSTRAINTS.values():
    device.validate()


# ==========================================================
# DEVICE ACCESS HELPERS
# ==========================================================

def get_device_constraint(
    device_name: str
) -> Optional[DeviceConstraint]:
    """
    Retrieve device constraint object.
    """

    return DEVICE_CONSTRAINTS.get(device_name)


# ==========================================================
# VALID START HOUR
# ==========================================================

def is_valid_start_hour(
    device_name: str,
    start_hour: int
) -> bool:
    """
    Check whether a device can start at a given hour.
    Handles overnight scheduling windows.
    """

    device = get_device_constraint(device_name)

    if device is None:
        return False

    # ------------------------------------------------------
    # RESTRICTED HOURS
    # ------------------------------------------------------

    if start_hour in device.restricted_hours:
        return False

    # ------------------------------------------------------
    # OVERNIGHT WINDOW
    # Example:
    # 22 -> 07
    # ------------------------------------------------------

    if (
        device.earliest_start_hour
        >
        device.latest_finish_hour
    ):

        return (
            start_hour >= device.earliest_start_hour
            or
            start_hour <= device.latest_finish_hour
        )

    # ------------------------------------------------------
    # NORMAL WINDOW
    # ------------------------------------------------------

    return (
        device.earliest_start_hour
        <= start_hour
        <= device.latest_finish_hour
    )


# ==========================================================
# PREFERRED HOURS
# ==========================================================

def is_preferred_hour(
    device_name: str,
    start_hour: int
) -> bool:
    """
    Check whether a start hour is preferred.
    """

    device = get_device_constraint(device_name)

    if device is None:
        return False

    return start_hour in device.preferred_hours


# ==========================================================
# DEVICE FLEXIBILITY SCORE
# ==========================================================

def calculate_flexibility_score(
    device_name: str
) -> float:
    """
    Estimate how flexible a device is
    for optimization shifting.
    """

    device = get_device_constraint(device_name)

    if device is None:
        return 0

    score = 0

    # ------------------------------------------------------
    # INTERRUPTIBLE BONUS
    # ------------------------------------------------------

    if device.interruptible:
        score += 3

    # ------------------------------------------------------
    # CARBON FLEXIBILITY
    # ------------------------------------------------------

    if device.carbon_sensitive:
        score += 2

    # ------------------------------------------------------
    # RENEWABLE FLEXIBILITY
    # ------------------------------------------------------

    if device.renewable_preference:
        score += 1

    # ------------------------------------------------------
    # COMFORT PENALTY
    # ------------------------------------------------------

    if device.comfort_sensitive:
        score -= 2

    # ------------------------------------------------------
    # PRIORITY WEIGHT
    # ------------------------------------------------------

    score += (4 - device.priority)

    return max(score, 0)


# ==========================================================
# ENERGY USAGE ESTIMATION
# ==========================================================

def calculate_energy_usage(
    device_name: str
) -> float:
    """
    Total estimated energy usage (kWh).
    """

    device = get_device_constraint(device_name)

    if device is None:
        return 0

    return round(
        device.power_kw
        * device.duration_hours,
        2
    )


# ==========================================================
# DEVICE SUMMARY TABLE
# ==========================================================

def generate_device_summary():

    rows = []

    for device in DEVICE_CONSTRAINTS.values():

        rows.append({

            "Device":
            device.name,

            "Category":
            device.category,

            "Power (kW)":
            device.power_kw,

            "Duration (hrs)":
            device.duration_hours,

            "Priority":
            device.priority,

            "Interruptible":
            device.interruptible,

            "Comfort Sensitive":
            device.comfort_sensitive,

            "Carbon Sensitive":
            device.carbon_sensitive

        })

    return rows


# ==========================================================
# TESTING
# ==========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("GRIDFLEX AI DEVICE CONSTRAINTS")
    print("===================================")

    for device_name in DEVICE_CONSTRAINTS:

        energy = calculate_energy_usage(
            device_name
        )

        flexibility = calculate_flexibility_score(
            device_name
        )

        print(f"\n{device_name}")

        print(f"Energy Usage: {energy} kWh")

        print(
            f"Flexibility Score: {flexibility}"
        )