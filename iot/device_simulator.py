import time
from datetime import datetime


DEVICE_REGISTRY = {

    "EV Charger": {

        "status": "OFF",

        "power_kw": 7.2,

        "energy_used_kwh": 0

    },

    "Washing Machine": {

        "status": "OFF",

        "power_kw": 1.2,

        "energy_used_kwh": 0

    },

    "Dishwasher": {

        "status": "OFF",

        "power_kw": 1.5,

        "energy_used_kwh": 0

    },

    "Immersion Heater": {

        "status": "OFF",

        "power_kw": 3.0,

        "energy_used_kwh": 0

    },

    "Air Conditioning": {

        "status": "OFF",

        "power_kw": 2.5,

        "energy_used_kwh": 0

    }

}


def get_device(device_name):

    if device_name not in DEVICE_REGISTRY:

        raise ValueError(
            f"Unknown device: "
            f"{device_name}"
        )

    return DEVICE_REGISTRY[device_name]



def turn_device_on(device_name):

    device = get_device(device_name)

    device["status"] = "ON"

    print(
        f"\n{device_name} -> ON"
    )


def turn_device_off(device_name):

    device = get_device(device_name)

    device["status"] = "OFF"

    print(
        f"{device_name} -> OFF"
    )



def update_energy_usage(

    device_name,
    runtime_hours

):

    device = get_device(device_name)

    energy = (

        device["power_kw"]

        * runtime_hours

    )

    device["energy_used_kwh"] += energy

    return round(energy, 2)


def execute_device(

    device_name,
    runtime_hours

):


    print(
        "GRIDFLEX AI DEVICE EXECUTION"
    )


    print(
        f"\nDevice: {device_name}"
    )

    print(
        f"Runtime: {runtime_hours} hours"
    )

    turn_device_on(device_name)

    print(
        "\nExecuting scheduled task..."
    )


    time.sleep(1)



    energy_used = update_energy_usage(

        device_name,
        runtime_hours

    )



    turn_device_off(device_name)


    print(
        "\nExecution Complete."
    )

    print(
        f"Energy Used: "
        f"{energy_used} kWh"
    )

    print(
        f"Timestamp: "
        f"{datetime.now()}"
    )



def display_all_devices():



    print(
        "DEVICE STATUS"
    )

    for name, info in DEVICE_REGISTRY.items():

        print(
            f"\n{name}"
        )

        print(
            f"Status: {info['status']}"
        )

        print(
            f"Power: {info['power_kw']} kW"
        )

        print(
            f"Total Energy Used: "
            f"{round(info['energy_used_kwh'], 2)} kWh"
        )



def reset_all_devices():

    for device in DEVICE_REGISTRY.values():

        device["status"] = "OFF"

        device["energy_used_kwh"] = 0

    print(
        "\nAll devices reset."
    )



if __name__ == "__main__":

    execute_device(

        device_name="EV Charger",

        runtime_hours=4

    )

    display_all_devices()