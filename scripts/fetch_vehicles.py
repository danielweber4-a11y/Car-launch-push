import os
import json


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
    Fetch vehicle data. This is a placeholder – replace with actual fetching logic.
    """
    # Example vehicle data
    return [
        {"name": "Toyota Corolla", "specs": "1.8L, 4-cylinder, 139 hp", "release_date": "2020-01-15", "image": "https://example.com/toyota_corolla.jpg"},
        {"name": "Volkswagen Golf", "specs": "1.4L TSI, 147 hp", "release_date": "2019-06-01", "image": "https://example.com/vw_golf.jpg"},
        {"name": "Tesla Model Y", "specs": "Dual Motor AWD, 384 hp", "release_date": "2023-03-10", "image": "https://example.com/tesla_model_y.jpg"},
    ]


if __name__ == '__main__':
    # Fetch vehicle data
    vehicles = fetch_vehicles()
    
    if vehicles:
        save_to_json_file(vehicles)
        print("Fetched and saved vehicles successfully.")
    else:
        print("No vehicles fetched.")
