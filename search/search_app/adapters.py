import requests
from django.conf import settings

class GooglePlacesAdapter:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def search_places(self, query, location, radius=5000):
        params = {
            'query': query,
            'location': location,
            'radius': radius,
            'key': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json().get('results', [])

class GoogleDistanceMatrixAdapter:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    def get_distances(self, origins, destinations, mode='walking', units='metric'):
        params = {
            'origins': origins,
            'destinations': "|".join(destinations),
            'mode': mode,
            'units': units,
            'key': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
