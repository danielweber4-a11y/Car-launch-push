import os
import json
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def filter_recent_vehicles(vehicles, days=7, current_time=None):
    """Return only vehicles whose release_date is within the last `days` days."""
    if current_time is None:
        current_time = datetime.now(tz=timezone.utc)
    cutoff = current_time - timedelta(days=days)
    recent = []
    for vehicle in vehicles:
        raw_date = vehicle.get("release_date")
        if not raw_date:
            logger.warning("Vehicle missing release_date; skipping. Record: %s", vehicle)
            continue
        parsed = None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(raw_date, fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        if parsed is None:
            logger.warning("Invalid release_date format %r; skipping. Record: %s", raw_date, vehicle)
            continue
        if parsed >= cutoff:
            recent.append(vehicle)
    return recent


def process_data(file_path, days=7):
    with open(file_path, "r") as file:
        data = json.load(file)

    data = filter_recent_vehicles(data, days=days)

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
