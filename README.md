# Car-launch-push
Beschreibung: "Ein Agent, der wöchentlich am freitag um 6 Uhr neue Fahrzeuge mit Bildern und Details auflistet und per E-Mail versendet."

## Data Sources / Databases

The `scripts/fetch_vehicles.py` script retrieves vehicle data from the following public databases and APIs:

| Source | URL | Description |
|--------|-----|-------------|
| **NHTSA vPIC API** | https://vpic.nhtsa.dot.gov/api/ | U.S. National Highway Traffic Safety Administration – Vehicle Product Information Catalog and Vehicle Listing (vPIC). Provides a complete, authoritative list of vehicle makes and models. No API key required. |
| **CarQuery API** | https://www.carqueryapi.com/ | Free public API for car makes, models, trims, and specifications. Includes country of origin and model year range data. No API key required. |
| **FuelEconomy.gov API** | https://www.fueleconomy.gov/ws/rest/ | U.S. EPA / Department of Energy fuel-economy data. Provides the list of makes available for each model year, making it especially useful for tracking newly introduced models. No API key required. |

### Endpoints used

```
# NHTSA – all registered makes
GET https://vpic.nhtsa.dot.gov/api/vehicles/GetAllMakes?format=json

# CarQuery – all makes (JSONP, wrapper stripped automatically)
GET https://www.carqueryapi.com/api/0.3/?cmd=getMakes

# FuelEconomy.gov – makes for the current model year
GET https://www.fueleconomy.gov/ws/rest/vehicle/menu/make?year=<current_year>
```

Results from all three sources are merged and saved to `data/fetched_data.json` after each run. Each record carries a `source` field indicating which API it came from. Individual source failures are logged as warnings and do not abort the run.
