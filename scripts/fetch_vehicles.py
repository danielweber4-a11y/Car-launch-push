import os
import re
import json
import requests
from datetime import datetime

# Data sources used by this script:
# 1. NHTSA vPIC API (https://vpic.nhtsa.dot.gov/api/)
#    - Free, public API provided by the U.S. National Highway Traffic Safety Administration
#    - Used to retrieve passenger car makes and models
# 2. CarQuery API (https://www.carqueryapi.com/)
#    - Free, public API for car makes, models, and trim data including model years
#    - Only passenger car body styles are included
# 3. FuelEconomy.gov API (https://www.fueleconomy.gov/ws/rest/)
#    - Free, public API provided by the U.S. EPA / Department of Energy
#    - Used to retrieve passenger car makes and models for the current model year
# 4. data/fetched_data.json – local cache of the last successful fetch

NHTSA_BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"
CARQUERY_BASE_URL = "https://www.carqueryapi.com/api/0.3/"
FUELECONOMY_BASE_URL = "https://www.fueleconomy.gov/ws/rest/vehicle"

# Passenger car body styles used to filter CarQuery results
PASSENGER_CAR_BODIES = {
    "Sedan", "Coupe", "Hatchback", "Wagon", "Convertible",
    "Cabriolet", "Targa", "Roadster",
}

# Maximum number of makes to query for models from NHTSA to avoid excessive API calls
MAX_MAKES_NHTSA = 50


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


def fetch_passenger_cars_nhtsa(year=None):
    """
    Fetch passenger car models from the NHTSA vPIC API.

    Database / API sources checked:
      - NHTSA vPIC API: https://vpic.nhtsa.dot.gov/api/
        Step 1: GET /vehicles/GetMakesForVehicleType/PassengerCar?format=json
          Returns only makes that manufacture passenger cars.
        Step 2: GET /vehicles/GetModelsForMakeIdYear/makeId/{id}/modelYear/{year}/vehicleType/Passenger Car?format=json
          Returns passenger car models for each make and the given model year.

    Returns a list of dicts with keys: oem, model, model_year, release_date, source.
    """
    if year is None:
        year = datetime.now().year

    makes_url = f"{NHTSA_BASE_URL}/GetMakesForVehicleType/PassengerCar?format=json"
    print(f"Fetching passenger car makes from: {makes_url}")
    try:
        response = requests.get(makes_url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch passenger car makes from {makes_url}: {exc}") from exc

    payload = response.json()
    if "Results" not in payload:
        raise ValueError(f"Unexpected response from {makes_url}: 'Results' key missing.")
    makes = payload["Results"]

    vehicles = []
    # Limit to MAX_MAKES_NHTSA makes to keep total API calls manageable
    for make in makes[:MAX_MAKES_NHTSA]:
        make_id = make.get("MakeId")
        make_name = make.get("MakeName", "")
        models_url = (
            f"{NHTSA_BASE_URL}/GetModelsForMakeIdYear/makeId/{make_id}"
            f"/modelYear/{year}/vehicleType/Passenger Car?format=json"
        )
        try:
            r = requests.get(models_url, timeout=30)
            r.raise_for_status()
            models = r.json().get("Results", [])
            for m in models:
                vehicles.append({
                    "oem": make_name,
                    "model": m.get("Model_Name", ""),
                    "model_year": year,
                    # Approximate launch date as start of model year; exact dates are not
                    # available from the NHTSA API.
                    "release_date": f"{year}-01-01",
                    "source": "NHTSA vPIC API",
                })
        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as exc:
            print(f"Warning: Could not fetch models for {make_name}: {exc}")

    print(f"Fetched {len(vehicles)} passenger car models from NHTSA vPIC API (year={year}).")
    return vehicles


def fetch_passenger_cars_carquery(year=None):
    """
    Fetch passenger car models from the CarQuery API, filtered by body style.

    Database / API sources checked:
      - CarQuery API: https://www.carqueryapi.com/
        Step 1: GET /?cmd=getMakes&year={year}
          Returns makes available for the given model year.
        Step 2: GET /?cmd=getModels&make={make}&year={year}
          Returns models for each make; only those with a passenger car body style
          (Sedan, Coupe, Hatchback, Wagon, Convertible, etc.) are kept.
        The responses are JSONP; this function strips the wrapper automatically.

    Returns a list of dicts with keys: oem, model, model_year, release_date, source.
    """
    if year is None:
        year = datetime.now().year

    makes_url = f"{CARQUERY_BASE_URL}?cmd=getMakes&year={year}"
    print(f"Fetching passenger car makes from: {makes_url}")
    try:
        response = requests.get(makes_url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch makes from CarQuery: {exc}") from exc

    text = response.text.strip()
    match = re.match(r'^\?\s*\(\s*(.*)\s*\)\s*;?\s*$', text, re.DOTALL)
    payload = json.loads(match.group(1)) if match else response.json()
    makes = payload.get("Makes", [])

    vehicles = []
    for make in makes:
        make_id = make.get("make_id", "")
        make_name = make.get("make_display", make_id)
        models_url = f"{CARQUERY_BASE_URL}?cmd=getModels&make={make_id}&year={year}"
        try:
            r = requests.get(models_url, timeout=30)
            r.raise_for_status()
            mtext = r.text.strip()
            mmatch = re.match(r'^\?\s*\(\s*(.*)\s*\)\s*;?\s*$', mtext, re.DOTALL)
            mpayload = json.loads(mmatch.group(1)) if mmatch else r.json()
            models = mpayload.get("Models", [])
            for m in models:
                body = m.get("model_body", "")
                if body not in PASSENGER_CAR_BODIES:
                    continue
                vehicles.append({
                    "oem": make_name,
                    "model": m.get("model_name", ""),
                    "model_year": year,
                    # Approximate launch date as start of model year; exact dates are not
                    # available from the CarQuery API.
                    "release_date": f"{year}-01-01",
                    "source": "CarQuery API",
                })
        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as exc:
            print(f"Warning: Could not fetch CarQuery models for {make_name}: {exc}")

    print(f"Fetched {len(vehicles)} passenger car models from CarQuery API (year={year}).")
    return vehicles


def fetch_passenger_cars_fueleconomy(year=None):
    """
    Fetch passenger car models from the FuelEconomy.gov (EPA) API for a given model year.

    Database / API sources checked:
      - FuelEconomy.gov API: https://www.fueleconomy.gov/ws/rest/
        Step 1: GET /vehicle/menu/make?year=<year>
          Returns makes with fuel-economy data for the specified model year.
        Step 2: GET /vehicle/menu/model?year=<year>&make=<make>
          Returns models for each make.
        Defaults to the current calendar year.

    Returns a list of dicts with keys: oem, model, model_year, release_date, source.
    """
    if year is None:
        year = datetime.now().year

    makes_url = f"{FUELECONOMY_BASE_URL}/menu/make?year={year}"
    print(f"Fetching passenger car makes from: {makes_url}")
    try:
        response = requests.get(makes_url, timeout=30, headers={"Accept": "application/json"})
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to fetch makes from FuelEconomy.gov: {exc}") from exc

    payload = response.json()
    items = payload.get("menuItem", [])
    if isinstance(items, dict):
        items = [items]

    vehicles = []
    for item in items:
        make_name = item.get("text", item.get("value", ""))
        models_url = f"{FUELECONOMY_BASE_URL}/menu/model?year={year}&make={requests.utils.quote(make_name)}"
        try:
            r = requests.get(models_url, timeout=30, headers={"Accept": "application/json"})
            r.raise_for_status()
            mpayload = r.json()
            models = mpayload.get("menuItem", [])
            if isinstance(models, dict):
                models = [models]
            for m in models:
                model_name = m.get("text", m.get("value", ""))
                vehicles.append({
                    "oem": make_name,
                    "model": model_name,
                    "model_year": year,
                    # Approximate launch date as start of model year; exact dates are not
                    # available from the FuelEconomy.gov API.
                    "release_date": f"{year}-01-01",
                    "source": f"FuelEconomy.gov API ({year})",
                })
        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as exc:
            print(f"Warning: Could not fetch FuelEconomy models for {make_name}: {exc}")

    print(f"Fetched {len(vehicles)} passenger car models from FuelEconomy.gov API (year={year}).")
    return vehicles


def fetch_vehicles():
    """
    Fetch passenger car models from all configured data sources and return the combined list.

    Only passenger cars are included; trucks, motorcycles, and other vehicle types
    are excluded at the source level.

    Sources:
      1. NHTSA vPIC API      – https://vpic.nhtsa.dot.gov/api/
      2. CarQuery API        – https://www.carqueryapi.com/
      3. FuelEconomy.gov API – https://www.fueleconomy.gov/ws/rest/

    Each source is queried independently.  Failures in individual sources are
    logged as warnings rather than hard errors so that the remaining sources can
    still contribute results.

    Returns a combined list of dicts with keys: oem, model, model_year, release_date, source.
    """
    all_vehicles = []

    for fetch_fn in (fetch_passenger_cars_nhtsa, fetch_passenger_cars_carquery, fetch_passenger_cars_fueleconomy):
        try:
            all_vehicles.extend(fetch_fn())
        except (RuntimeError, ValueError, requests.exceptions.RequestException) as exc:
            print(f"Warning: {fetch_fn.__name__} failed and will be skipped: {exc}")

    print(f"Total passenger car models fetched from all sources: {len(all_vehicles)}")
    return all_vehicles


if __name__ == '__main__':
    # Fetch passenger car data from all sources
    vehicles = fetch_vehicles()

    if vehicles:
        save_to_json_file(vehicles)
        print("Fetched and saved vehicles successfully.")
    else:
        print("No vehicles fetched.")
