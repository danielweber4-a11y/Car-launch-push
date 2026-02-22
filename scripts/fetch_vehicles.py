import os
import json


class VehicleFetcher:
    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.ensure_data_directory_exists()

    def ensure_data_directory_exists(self):
        os.makedirs(self.data_directory, exist_ok=True)

    def fetch_vehicles(self):
        # Assuming you have a method to get vehicle data
        vehicles = self.get_vehicle_data()  # This should return a list of vehicle data
        self.save_to_json(vehicles)

    def get_vehicle_data(self):
        # Placeholder: Actual implementation to fetch vehicle data
        return []  # Return list of vehicle data

    def save_to_json(self, vehicles):
        json_data = self.construct_json(vehicles)
        file_path = os.path.join(self.data_directory, 'vehicles.json')
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

    def construct_json(self, vehicles):
        # Construct the JSON structure dynamically
        return {'vehicles': vehicles}


if __name__ == '__main__':
    fetcher = VehicleFetcher(data_directory='./data/')
    fetcher.fetch_vehicles()