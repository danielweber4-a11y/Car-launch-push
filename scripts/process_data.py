import os
import json
import logging

logger = logging.getLogger(__name__)

def process_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    processed_data = []
    for car in data:
        missing = [key for key in ("name", "specs", "release_date", "image") if key not in car]
        if missing:
            logger.warning("Record missing required fields %s; using defaults. Record: %s", missing, car)
        processed_data.append(
            f"Name: {car.get('name', 'Unknown')}\n"
            f"Specs: {car.get('specs', 'Unknown')}\n"
            f"Release Date: {car.get('release_date', 'Unknown')}\n"
            f"Image URL: {car.get('image', 'Unknown')}\n\n"
        )

    return "\n".join(processed_data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    here = os.path.dirname(__file__)
    json_path = os.path.join(here, "..", "data", "fetched_data.json")
    result = process_data(json_path)
    print("Processed data:\n", result)
