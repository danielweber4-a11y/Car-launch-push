import json

def process_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    
    processed_data = []
    for car in data:
        processed_data.append(f"Name: {car['name']}\nSpecs: {car['specs']}\nRelease Date: {car['release_date']}\nImage URL: {car['image']}\n\n")
    
    return "\n".join(processed_data)

if __name__ == "__main__":
    result = process_data("../data/fetched_data.json")
    print("Processed data:\n", result)