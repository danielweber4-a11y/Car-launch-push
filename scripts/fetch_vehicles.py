import os
import json

# Ensure the 'data' directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Set the file path dynamically
file_path = os.path.join('data', 'fetched_data.json')

# A function to fetch vehicle data and save it to the json file
def fetch_vehicle_data():
    # Your existing logic to fetch data
    vehicles = []  # Example data fetching logic

    # Write data to the json file
    with open(file_path, 'w') as json_file:
        json.dump(vehicles, json_file, indent=4)

# Call the function
fetch_vehicle_data()