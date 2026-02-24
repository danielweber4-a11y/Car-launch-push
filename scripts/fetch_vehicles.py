import os
import re
import json
import requests
from datetime import datetime

# Data sources used by this script:
# 1. NHTSA vPIC API (https://vpic.nhtsa.dot.gov/api/)
#    - Free, public API provided by the U.S. National Highway Traffic Safety Administration
#    - Used to retrieve vehicle makes and models
# 2. CarQuery API (https://www.carqueryapi.com/)
#    - Free, public API for car makes, models, and trim data including model years
# 3. FuelEconomy.gov API (https://www.fueleconomy.gov/ws/rest/)
#    - Free, public API provided by the U.S. EPA / Department of Energy
#    - Used to retrieve vehicle makes available for the current model year
# 4. data/fetched_data.json – local cache of the last successful fetch

NHTSA_BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"
CARQUERY_BASE_URL = "https://www.carqueryapi.com/api/0.3/"
FUELECONOMY_BASE_URL = "https://www.fueleconomy.gov/ws/rest/vehicle"


def get_data_path():
    """
    Get the absolute path to the fetched_data.json file inside the data directory.
    """
    # Get the absolute path of the current script
    current_script_path = os.path.abspath(__file__)
    # Navigate to the parent directory of the current script
    base_dir = os.path.dirname(current_script_path)
    # Get the path to the "data" directory
    data_dir = os.path.join(base_dir, "..", "data")
    
    # Ensure the "data" directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Return the absolute path to the fetched_data.json file
    return os.path.join(data_dir, "fetched_data.json")


def save_to_json_file(data):
    """
    Save the provided data to the file at the data path.
    """
    file_path = get_data_path()
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Data saved to {file_path}")


def fetch_vehicles_nhtsa():
    """
    Fetch vehicle makes from the NHTSA vPIC API.

    Database / API sources checked:
      - NHTSA vPIC API: https://vpic.nhtsa.dot.gov/api/
        Endpoint used: GET /vehicles/GetAllMakes?format=json
        Returns the full list of vehicle makes recognised by the NHTSA.

    Returns a list of dicts with keys: make_id, make_name, source.
    """
    url = f"{NHTSA_BASE_URL}/GetAllMakes?format=json"
    print(f"Fetching vehicle data from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch vehicle data from {url}: {exc}") from exc
    payload = response.json()
    if "Results" not in payload:
        raise ValueError(f"Unexpected response from {url}: 'Results' key missing. Got: {list(payload.keys())}")
    results = payload["Results"]
    vehicles = [
        {"make_id": item["Make_ID"], "make_name": item["Make_Name"], "source": "NHTSA vPIC API"}
        for item in results
    ]
    print(f"Fetched {len(vehicles)} vehicle makes from NHTSA vPIC API.")
    return vehicles


def fetch_vehicles_carquery():
    """
    Fetch vehicle makes from the CarQuery API.

    Database / API sources checked:
      - CarQuery API: https://www.carqueryapi.com/
        Endpoint used: GET /?cmd=getMakes
        Returns makes with country of origin and year range data.
        The response is JSONP; this function strips the wrapper automatically.

    Returns a list of dicts with keys: make_id, make_name, source.
    """
    url = f"{CARQUERY_BASE_URL}?cmd=getMakes"
    print(f"Fetching vehicle data from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch vehicle data from {url}: {exc}") from exc

    # CarQuery returns JSONP: ?( { "Makes": [...] } );
    text = response.text.strip()
    match = re.match(r'^\?\s*\(\s*(.*)\s*\)\s*;?\s*$', text, re.DOTALL)
    if match:
        payload = json.loads(match.group(1))
    else:
        payload = response.json()

    makes = payload.get("Makes", [])
    vehicles = [
        {
            "make_id": item.get("make_id", ""),
            "make_name": item.get("make_display", item.get("make_id", "")),
            "source": "CarQuery API",
        }
        for item in makes
    ]
    print(f"Fetched {len(vehicles)} vehicle makes from CarQuery API.")
    return vehicles


def fetch_vehicles_fueleconomy(year=None):
    """
    Fetch vehicle makes from the FuelEconomy.gov (EPA) API for a given model year.

    Database / API sources checked:
      - FuelEconomy.gov API: https://www.fueleconomy.gov/ws/rest/
        Endpoint used: GET /vehicle/menu/make?year=<year>
        Returns makes with fuel-economy data for the specified model year.
        Defaults to the current calendar year.

    Returns a list of dicts with keys: make_id, make_name, source.
    """
    if year is None:
        year = datetime.now().year
    url = f"{FUELECONOMY_BASE_URL}/menu/make?year={year}"
    print(f"Fetching vehicle data from: {url}")
    try:
        response = requests.get(url, timeout=30, headers={"Accept": "application/json"})
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch vehicle data from {url}: {exc}") from exc
    payload = response.json()
    items = payload.get("menuItem", [])
    # menuItem may be a single dict rather than a list when only one result is returned
    if isinstance(items, dict):
        items = [items]
    vehicles = [
        {
            "make_id": item.get("value", ""),
            "make_name": item.get("text", item.get("value", "")),
            "source": f"FuelEconomy.gov API ({year})",
        }
        for item in items
    ]
    print(f"Fetched {len(vehicles)} vehicle makes from FuelEconomy.gov API (year={year}).")
    return vehicles


def fetch_vehicles():
    """
    Fetch vehicle makes from all configured data sources and return the combined list.

    Sources:
      1. NHTSA vPIC API      – https://vpic.nhtsa.dot.gov/api/
      2. CarQuery API        – https://www.carqueryapi.com/
      3. FuelEconomy.gov API – https://www.fueleconomy.gov/ws/rest/

    Each source is queried independently.  Failures in individual sources are
    logged as warnings rather than hard errors so that the remaining sources can
    still contribute results.

    Returns a combined list of dicts with keys: make_id, make_name, source.
    """
    all_vehicles = []

    for fetch_fn in (fetch_vehicles_nhtsa, fetch_vehicles_carquery, fetch_vehicles_fueleconomy):
        try:
            all_vehicles.extend(fetch_fn())
        except (RuntimeError, ValueError, requests.exceptions.RequestException) as exc:
            print(f"Warning: {fetch_fn.__name__} failed and will be skipped: {exc}")

    print(f"Total vehicle makes fetched from all sources: {len(all_vehicles)}")
    return all_vehicles


if __name__ == '__main__':
    # Fetch vehicle data from all sources
    vehicles = fetch_vehicles()

    if vehicles:
        save_to_json_file(vehicles)
        print("Fetched and saved vehicles successfully.")
    else:
        print("No vehicles fetched.")
