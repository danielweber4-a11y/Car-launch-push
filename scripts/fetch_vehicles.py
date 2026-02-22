import os
import json


def get_data_path():
    # Get the correct file path for the data directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(base_dir, 'data')
    # Create the data directory if it doesn't exist
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    return os.path.join(data_directory, 'fetched_data.json')


def save_to_json_file(data):
    with open(get_data_path(), 'w') as json_file:
        json.dump(data, json_file)


def fetch_vehicles():
    # Example vehicle data
    data = {
        'vehicles': [
            {'make': 'Toyota', 'model': 'Camry', 'year': 2020},
            {'make': 'Honda', 'model': 'Civic', 'year': 2019}
        ]
    }
    return data
