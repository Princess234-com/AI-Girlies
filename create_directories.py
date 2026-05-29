from pathlib import Path


def create_project_directories():

    directories = [

        "data/raw",
        "data/processed",
        "data/predictions",

        "forecasting",
        "optimization",
        "regional",
        "scheduler",
        "models",
        "utils"

    ]

    for directory in directories:

        Path(directory).mkdir(
            parents=True,
            exist_ok=True
        )

    print("Project directories created successfully.")


if __name__ == "__main__":

    create_project_directories()