
from dataclasses import dataclass
from typing import Dict

@dataclass
class RegionalConfig:

    region_name: str

    demand_weight: float

    price_multiplier: float

    renewable_factor: float

    congestion_factor: float

    economic_factor: float

    volatility: float

    carbon_intensity_factor: float

    local_renewable_bias: float

    population_scaling: float

    volatility: float



REGIONAL_CONFIG: Dict[str, RegionalConfig] = {

    "London": RegionalConfig(

        region_name="London",

        demand_weight=0.16,

        price_multiplier=1.20,

        renewable_factor=0.72,

        congestion_factor=1.30,

        economic_factor=1.25,

        volatility=0.07,

        carbon_intensity_factor=1.15,

        local_renewable_bias=0.85,

        population_scaling=1.25

    ),

    "South_East": RegionalConfig(

        region_name="South East",

        demand_weight=0.14,

        price_multiplier=1.10,

        renewable_factor=0.85,

        congestion_factor=1.12,

        economic_factor=1.10,

        volatility=0.05,

        carbon_intensity_factor=1.00,

        local_renewable_bias=0.95,

        population_scaling=1.10

    ),

    "Midlands": RegionalConfig(

        region_name="Midlands",

        demand_weight=0.13,

        price_multiplier=1.00,

        renewable_factor=1.00,

        congestion_factor=1.00,

        economic_factor=1.00,

        volatility=0.04,

        carbon_intensity_factor=0.95,

        local_renewable_bias=1.00,

        population_scaling=1.00

    ),


    "North_West": RegionalConfig(

        region_name="North West",

        demand_weight=0.11,

        price_multiplier=0.95,

        renewable_factor=1.18,

        congestion_factor=0.90,

        economic_factor=0.92,

        volatility=0.05,

        carbon_intensity_factor=0.82,

        local_renewable_bias=1.15,

        population_scaling=0.95

    ),


    "Scotland": RegionalConfig(

        region_name="Scotland",

        demand_weight=0.10,

        price_multiplier=0.88,

        renewable_factor=1.40,

        congestion_factor=0.82,

        economic_factor=0.85,

        volatility=0.07,

        carbon_intensity_factor=0.65,

        local_renewable_bias=1.35,

        population_scaling=0.85

    ),


    "Wales": RegionalConfig(

        region_name="Wales",

        demand_weight=0.07,

        price_multiplier=0.92,

        renewable_factor=1.28,

        congestion_factor=0.88,

        economic_factor=0.90,

        volatility=0.05,

        carbon_intensity_factor=0.78,

        local_renewable_bias=1.20,

        population_scaling=0.90

    ),


    "South_West": RegionalConfig(

        region_name="South West",

        demand_weight=0.09,

        price_multiplier=0.96,

        renewable_factor=1.22,

        congestion_factor=0.93,

        economic_factor=0.94,

        volatility=0.05,

        carbon_intensity_factor=0.80,

        local_renewable_bias=1.18,

        population_scaling=0.92

    )

}


def get_region_config(region_name: str):


    return REGIONAL_CONFIG.get(region_name)


def get_all_regions():


    return list(REGIONAL_CONFIG.keys())


def validate_regional_weights():


    total_weight = sum(

        region.demand_weight

        for region in REGIONAL_CONFIG.values()

    )

    print("REGIONAL CONFIG VALIDATION")


    print(f"\nTotal Regional Weight: {round(total_weight, 3)}")

    if total_weight > 1.20:

        print("WARNING: Regional weights too high.")

    elif total_weight < 0.70:

        print("WARNING: Regional weights too low.")

    else:

        print("Regional weights validated.")



def display_region_summary():

    print("GRIDFLEX AI REGIONAL CONFIG")

    for region_name, config in REGIONAL_CONFIG.items():

        print(f"\n{region_name}")

        print(
            f"Demand Weight: "
            f"{config.demand_weight}"
        )

        print(
            f"Price Multiplier: "
            f"{config.price_multiplier}"
        )

        print(
            f"Renewable Factor: "
            f"{config.renewable_factor}"
        )

        print(
            f"Congestion Factor: "
            f"{config.congestion_factor}"
        )

        print(
            f"Volatility: "
            f"{config.volatility}"
        )

        print(
            f"Carbon Intensity: "
            f"{config.carbon_intensity_factor}"
        )


if __name__ == "__main__":

    validate_regional_weights()

    display_region_summary()