import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_vehicles():
    url = 'https://www.autobild.de'  # Website von AutoBild
    
    try:
        # HTTP GET-Anfrage an die AutoBild-Seite
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Löst Fehler aus, wenn HTTP-Antwort ungültig ist (4xx/5xx)
        
        # HTML-Inhalte parsen
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Fahrzeugdaten scrapen (dieser Code ist ein Beispiel – passe ihn an die AutoBild-Seite an)
        vehicles = []
        for article in soup.find_all("article", class_="article"):  # Passe den Selector an die Struktur der Seite an
            try:
                title = article.find("h2").get_text(strip=True)  # Fahrzeugname
                link = article.find("a")["href"]  # Link zur Fahrzeugbeschreibung
                vehicles.append({"title": title, "link": link})
            except (AttributeError, TypeError):
                continue  # Überspringe Artikel ohne die erwartete Struktur
        
        # Gesammelte Daten ausgeben
        logging.info(f"Scraped {len(vehicles)} vehicles.")
        print(f"Scraped {len(vehicles)} vehicles.")
        return vehicles

    except requests.exceptions.RequestException as e:
        # Netzwerkfehler protokollieren
        logging.error(f"Error fetching vehicles: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return []

# Beispielnutzung
if __name__ == '__main__':
    vehicles = fetch_vehicles()
    if vehicles:
        for vehicle in vehicles:
            print(f"Title: {vehicle['title']}, Link: {vehicle['link']}")
    else:
        print("Keine Fahrzeuge gefunden oder ein Fehler ist aufgetreten.")