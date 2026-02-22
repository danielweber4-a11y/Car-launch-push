import requests
from bs4 import BeautifulSoup

def fetch_vehicles(url):
    response = requests.get(url)
    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    vehicles = []
    
    # Extract vehicle information from the HTML soup (modify selectors as needed)
    for vehicle in soup.select('.vehicle'):  # example selector
        title = vehicle.select_one('.title').text.strip()  # example selector
        price = vehicle.select_one('.price').text.strip()  # example selector
        vehicles.append({'title': title, 'price': price})
    
    return vehicles

# Example Usage
# vehicles_list = fetch_vehicles('http://example.com/vehicles')
# print(vehicles_list)