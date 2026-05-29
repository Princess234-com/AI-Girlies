from datetime import datetime

from iot.device_simulator import (

    execute_device,
    get_device

)

VALID_COMMANDS = [

    "START_DEVICE",
    "STOP_DEVICE"

]



def validate_command(

    device_name,
    command

):

    try:

        get_device(device_name)

    except Exception as e:

        raise ValueError(
            f"Invalid device: "
            f"{device_name}"
        )


    if command not in VALID_COMMANDS:

        raise ValueError(
            f"Invalid command: "
            f"{command}"
        )


def create_command_payload(

    device_name,
    command,
    runtime_hours

):

    payload = {

        "timestamp":
        str(datetime.now()),

        "device":
        device_name,

        "command":
        command,

        "runtime_hours":
        runtime_hours

    }

    return payload



def send_command(

    device_name,
    command,
    runtime_hours

):

    # ==================================================
    # VALIDATION
    # ==================================================

    validate_command(

        device_name,
        command

    )

    # ==================================================
    # PAYLOAD
    # ==================================================

    payload = create_command_payload(

        device_name,
        command,
        runtime_hours

    )

    print(
        "\n=================================="
    )

    print(
        "GRIDFLEX AI COMMAND DISPATCH"
    )

    print(
        "=================================="
    )

    print(
        f"\nDispatching command..."
    )

    print(
        f"\nPayload:\n{payload}"
    )

    # ==================================================
    # EXECUTE COMMAND
    # ==================================================

    if command == "START_DEVICE":

        execute_device(

            device_name,
            runtime_hours

        )

    elif command == "STOP_DEVICE":

        print(
            f"\n{device_name} stop command received."
        )

    # ==================================================
    # ACKNOWLEDGEMENT
    # ==================================================

    response = {

        "status": "SUCCESS",

        "device": device_name,

        "command": command,

        "timestamp": str(datetime.now()),

        "message":
        "Command executed successfully."

    }

    print(
        "\nAcknowledgement:"
    )

    print(response)

    return response


# ======================================================
# AUTOMATIC EXECUTION
# ======================================================

def automatic_dispatch(

    appliance_name,
    runtime_hours

):

    print(
        "\nAutomatic scheduling enabled."
    )

    response = send_command(

        device_name=
        appliance_name,

        command=
        "START_DEVICE",

        runtime_hours=
        runtime_hours

    )

    return response


# ======================================================
# MANUAL EXECUTION
# ======================================================

def manual_dispatch(

    appliance_name,
    runtime_hours

):

    print(
        "\nManual scheduling selected."
    )

    response = send_command(

        device_name=
        appliance_name,

        command=
        "START_DEVICE",

        runtime_hours=
        runtime_hours

    )

    return response


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    automatic_dispatch(

        appliance_name="EV Charger",

        runtime_hours=4

    )