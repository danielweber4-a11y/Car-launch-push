import os
import json
import requests

# Data sources used by this script:
# 1. NHTSA vPIC API (https://vpic.nhtsa.dot.gov/api/)
#    - Free, public API provided by the U.S. National Highway Traffic Safety Administration
#    - Used to retrieve vehicle makes and models
# 2. data/fetched_data.json – local cache of the last successful fetch

NHTSA_BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"


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


def fetch_vehicles():
    """
    Fetch vehicle data from the NHTSA vPIC API.

    Database / API sources checked:
      - NHTSA vPIC API: https://vpic.nhtsa.dot.gov/api/
        Endpoint used: GET /vehicles/GetAllMakes?format=json
        Returns the full list of vehicle makes recognised by the NHTSA.

    Returns a list of dicts with keys: make_id, make_name.
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
        {"make_id": item["Make_ID"], "make_name": item["Make_Name"]}
        for item in results
    ]
    print(f"Fetched {len(vehicles)} vehicle makes from NHTSA vPIC API.")
    return vehicles


if __name__ == '__main__':
    # Fetch vehicle data
    vehicles = fetch_vehicles()
    
    if vehicles:
        save_to_json_file(vehicles)
        print("Fetched and saved vehicles successfully.")
    else:
        print("No vehicles fetched.")
