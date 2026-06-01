import os
import requests
from datetime import datetime


BASE_DATASET_URL = (
    "https://api.neso.energy/dataset/"
    "8f2fe0af-871c-488d-8bad-960426f24601/"
    "resource/{resource_id}/download/{filename}"
)


RESOURCE_IDS = {

    2010: (
        "b3eae4a5-8c3c-4df1-b9de-7db243ac3a09",
        "demanddata_2010.csv"
    ),

    2011: (
        "01522076-2691-4140-bfb8-c62284752efd",
        "demanddata_2011.csv"
    ),

    2012: (
        "4bf713a2-ea0c-44d3-a09a-63fc6a634b00",
        "demanddata_2012.csv"
    ),

    2013: (
        "2ff7aaff-8b42-4c1b-b234-9446573a1e27",
        "demanddata_2013.csv"
    ),

    2014: (
        "b9005225-49d3-40d1-921c-03ee2d83a2ff",
        "demanddata_2014.csv"
    ),

    2015: (
        "cc505e45-65ae-4819-9b90-1fbb06880293",
        "demanddata_2015.csv"
    ),

    2016: (
        "3bb75a28-ab44-4a0b-9b1c-9be9715d3c44",
        "demanddata_2016.csv"
    ),

    2017: (
        "2f0f75b8-39c5-46ff-a914-ae38088ed022",
        "demanddata_2017.csv"
    ),

    2018: (
        "fcb12133-0db0-4f27-a4a5-1669fd9f6d33",
        "demanddata_2018.csv"
    ),

    2019: (
        "dd9de980-d724-415a-b344-d8ae11321432",
        "demanddata_2019.csv"
    ),

    2020: (
        "33ba6857-2a55-479f-9308-e5c4c53d4381",
        "demanddata_2020.csv"
    ),

    2021: (
        "18c69c42-f20d-46f0-84e9-e279045befc6",
        "demanddata_2021.csv"
    ),

    2022: (
        "bb44a1b5-75b1-4db2-8491-257f23385006",
        "demanddata_2022.csv"
    ),

    2023: (
        "bf5ab335-9b40-4ea4-b93a-ab4af7bce003",
        "demanddata_2023.csv"
    ),

    2024: (
        "f6d02c0f-957b-48cb-82ee-09003f2ba759",
        "demanddata_2024.csv"
    ),

    2025: (
        "b2bde559-3455-4021-b179-dfe60c0337b0",
        "demanddata_2025.csv"
    ),

    2026: (
        "8a4a771c-3929-4e56-93ad-cdf13219dea5",
        "demanddata_2026.csv"
    )
}



RAW_DATA_FOLDER = "data/raw"


def download_year(year):

    if year not in RESOURCE_IDS:

        print(f"No resource found for {year}")
        return

    resource_id, filename = RESOURCE_IDS[year]

    url = BASE_DATASET_URL.format(
        resource_id=resource_id,
        filename=filename
    )

    print(f"Downloading {year}...")

    response = requests.get(url)

    if response.status_code == 200:

        save_path = os.path.join(
            RAW_DATA_FOLDER,
            filename
        )

        with open(save_path, "wb") as file:

            file.write(response.content)

        print(f"Saved: {save_path}")

    else:

        print(
            f"Failed to download {year}"
        )


def download_all_years():

    current_year = datetime.now().year

    for year in range(2010, current_year + 1):

        download_year(year)


if __name__ == "__main__":

    download_all_years()