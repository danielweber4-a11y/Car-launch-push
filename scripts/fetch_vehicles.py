import os
import json

def get_data_path():
    """
    Ermittelt dynamisch den absoluten Pfad zur Datei fetched_data.json im data-Verzeichnis.
    Erstellt das data-Verzeichnis, wenn es nicht existiert.
    """
    # Absoluter Pfad des aktuellen Skripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '../data')  # Relativer Pfad eine Ebene höher und ins data-Verzeichnis

    # Erstellt den data-Ordner, falls nicht existiert
    os.makedirs(data_dir, exist_ok=True)

    # Gibt den absoluten Pfad zur fetched_data.json zurück
    return os.path.join(data_dir, 'fetched_data.json')


def save_to_json_file(data):
    """
    Speichert gegebene Daten in der Datei fetched_data.json im data-Verzeichnis.
    """
    json_file_path = get_data_path()
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"Daten wurden erfolgreich in {json_file_path} gespeichert.")


def fetch_vehicles():
    """
    Simuliert das Abrufen von Fahrzeugdaten und speichert die Daten in fetched_data.json.
    """
    # Platzhalter für echte Fahrzeugdaten (du kannst deine Logik hier einfügen)
    vehicles = [
        {'make': 'Toyota', 'model': 'Corolla', 'year': 2020},
        {'make': 'Honda', 'model': 'Civic', 'year': 2018},
        {'make': 'Tesla', 'model': 'Model 3', 'year': 2023}
    ]

    return vehicles


if __name__ == '__main__':
    # Fahrzeugdaten abrufen
    vehicle_data = fetch_vehicles()
    if vehicle_data:
        save_to_json_file(vehicle_data)
        print("Fahrzeugdaten abgerufen und gespeichert.")
    else:
        print("Keine Fahrzeugdaten gefunden oder ein Fehler ist aufgetreten.")
