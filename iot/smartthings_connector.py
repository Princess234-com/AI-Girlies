import uuid
from datetime import datetime


# ======================================================
# MOCK SMARTTHINGS API
# ======================================================

class SmartThingsConnector:

    def __init__(self):

        self.platform_name = (
            "Samsung SmartThings"
        )

        self.connected = False

    # ==================================================
    # CONNECT
    # ==================================================

    def connect(self):

        self.connected = True

        print(
            "\n========================="
        )

        print(
            "SMARTTHINGS CONNECTION"
        )

        print(
            "========================="
        )

        print(
            f"Connected to "
            f"{self.platform_name}"
        )

    # ==================================================
    # SEND COMMAND
    # ==================================================

    def send_command(

        self,

        device_name,

        action,

        execution_time

    ):

        if not self.connected:

            print(
                "Platform not connected."
            )

            return

        command_id = str(
            uuid.uuid4()
        )

        timestamp = (
            datetime.now()
        )

        print(
            "\n========================="
        )

        print(
            "SMARTTHINGS COMMAND"
        )

        print(
            "========================="
        )

        print(
            f"Command ID: "
            f"{command_id}"
        )

        print(
            f"Device: "
            f"{device_name}"
        )

        print(
            f"Action: "
            f"{action}"
        )

        print(
            f"Execution Time: "
            f"{execution_time}"
        )

        print(
            f"Timestamp: "
            f"{timestamp}"
        )

        print(
            "\nCloud acknowledgement received."
        )

        return {

            "command_id":
            command_id,

            "status":
            "accepted"

        }

    # ==================================================
    # DISCONNECT
    # ==================================================

    def disconnect(self):

        self.connected = False

        print(
            "\nDisconnected "
            "from SmartThings."
        )


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    connector = (
        SmartThingsConnector()
    )

    connector.connect()

    connector.send_command(

        device_name=
        "EV Charger",

        action=
        "START",

        execution_time=
        "01:00"

    )

    connector.disconnect()