import requests

url = "https://api.neso.energy/api/3/action/datapackage_show?id=historic-demand-data"
data = requests.get(url).json()

paths = [res["path"] for res in data["result"]["resources"]]
print(paths)
