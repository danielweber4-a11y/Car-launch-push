# Car-launch-push
Beschreibung: "Ein Agent, der wöchentlich am freitag um 6 Uhr neue Fahrzeuge mit Bildern und Details auflistet und per E-Mail versendet."

## Data Sources / Databases

The `scripts/fetch_vehicles.py` script retrieves vehicle data from the following public databases and APIs:

| Source | URL | Description |
|--------|-----|-------------|
| **NHTSA vPIC API** | https://vpic.nhtsa.dot.gov/api/ | U.S. National Highway Traffic Safety Administration – Vehicle Product Information Catalog and Vehicle Listing (vPIC). Provides a complete, authoritative list of vehicle makes and models. No API key required. |

### Endpoint used

```
GET https://vpic.nhtsa.dot.gov/api/vehicles/GetAllMakes?format=json
```

Returns all vehicle makes registered with the NHTSA. The fetched data is saved locally to `data/fetched_data.json` after each run.
