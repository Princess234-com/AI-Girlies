import requests


API_URL = (
    "https://api.neso.energy/"
    "api/3/action/datapackage_show"
    "?id=historic-demand-data"
)


def fetch_resource_ids():

    response = requests.get(API_URL)

    data = response.json()

    resources = data["result"]["resources"]

    resource_map = {}

    for resource in resources:

        name = resource["name"]

        if "Historic Demand Data" in name:

            try:

                year = int(
                    name.split()[-1]
                )

                resource_map[year] = {

                    "resource_id":
                        resource["id"],

                    "filename":
                        resource["url"].split("/")[-1]
                }

            except:
                continue

    return resource_map


if __name__ == "__main__":

    resource_map = fetch_resource_ids()

    for year, info in sorted(resource_map.items()):

        print(
            year,
            info["resource_id"],
            info["filename"]
        ) 