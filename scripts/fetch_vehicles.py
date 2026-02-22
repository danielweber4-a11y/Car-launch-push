import requests
from bs4 import BeautifulSoup
import json

def fetch_vehicles():
    url = "https://example-auto-news.com"  # Ersetze durch eine tatsächliche Quelle
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Beispiel für das Scrapen
    vehicles = []
    for item in soup.select(".vehicle-container"):
        car = {
            "name": item.find("h2").text.strip(),
            "image": item.find("img")["src"],
            "specs": item.find("p", class_="specs").text.strip(),
            "release_date": item.find("span", class_="release-date").text.strip()
        }
        vehicles.append(car)

    # Ergebnis speichern
    with open("../data/fetched_data.json", "w") as file:
        json.dump(vehicles, file, indent=4)

    return vehicles

if __name__ == "__main__":
    data = fetch_vehicles()
    print("Fetched vehicles:", len(data))