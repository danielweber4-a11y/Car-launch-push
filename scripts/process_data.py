import os
import json

def process_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    processed_data = []
    for car in data:
        processed_data.append(
            f"Name: {car['name']}\n"
            f"Specs: {car['specs']}\n"
            f"Release Date: {car['release_date']}\n"
            f"Image URL: {car['image']}\n\n"
        )

    return "\n".join(processed_data)

if __name__ == "__main__":
    here = os.path.dirname(__file__)
    json_path = os.path.join(here, "..", "data", "fetched_data.json")
    result = process_data(json_path)
    print("Processed data:\n", result)
