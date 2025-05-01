import requests

# Sample locations (real world places)
locations = [
    {
        "name": "Eiffel Tower",
        "description": "Famous landmark in Paris",
        "latitude": 48.8584,
        "longitude": 2.2945
    },
    {
        "name": "Times Square",
        "description": "Bustling commercial intersection",
        "latitude": 40.7580,
        "longitude": -73.9855
    },
    {
        "name": "Sydney Opera House",
        "description": "Iconic performing arts venue",
        "latitude": -33.8568,
        "longitude": 151.2153
    },
    {
        "name": "Tokyo Tower",
        "description": "Communications and observation tower",
        "latitude": 35.6586,
        "longitude": 139.7454
    }
]

# Add locations via API
for location in locations:
    response = requests.post(
        "http://localhost:8000/locations/",
        json=location
    )
    print(f"Added {location['name']}: {response.status_code}")