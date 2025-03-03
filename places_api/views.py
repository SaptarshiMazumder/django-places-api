from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

import requests

from .models import SearchHistory, RecommendedPlace
from .serializers import SearchHistorySerializer



class PlaceSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        query = request.query_params.get('q')
        if not query:
            return Response({"error": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Geolocation: determine user latitude and longitude
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        if lat and lng:
            try:
                user_lat = float(lat); user_lng = float(lng)
            except ValueError:
                return Response({"error": "Invalid latitude/longitude format."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_ip = request.META.get('REMOTE_ADDR')
            user_lat = user_lng = None
            # TODO: Use IP geolocation service to get actual location from IP.
            # For now, use a default location as a fallback.
            user_lat = 35.6895; user_lng = 139.6917  # Example: Tokyo coordinates

        # Call Google Places Text Search API to find places for the query near the location
        # google_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
        google_api_key = settings.GOOGLE_MAPS_API_KEY
        if not google_api_key:
            return Response({"error": "Server Google API key not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        places_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'location': f"{user_lat},{user_lng}",
            'radius': 5000,
            'key': google_api_key
        }
        try:
            resp = requests.get(places_url, params=params); data = resp.json()
        except Exception as e:
            return Response({"error": f"Places API request failed: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        results = data.get('results', [])
        if not results:
            return Response({"message": "No places found for the given query."}, status=status.HTTP_200_OK)
        top_results = results[:5]

        processed_places = []
        destinations = []
        for place in top_results:
            name = place.get('name')
            address = place.get('formatted_address') or place.get('vicinity', '')
            rating = place.get('rating')
            user_ratings = place.get('user_ratings_total')
            loc = place.get('geometry', {}).get('location', {})
            place_lat = loc.get('lat'); place_lng = loc.get('lng')
            if place_lat and place_lng:
                destinations.append(f"{place_lat},{place_lng}")
            processed_places.append({
                "name": name,
                "address": address,
                "rating": rating,
                "user_ratings_count": user_ratings,
                "latitude": place_lat,
                "longitude": place_lng,
                "description": "",
                "review_summary": "",
                "distance_m": None,
                "walking_time_min": None,
                "is_best": False
            })

        # Call Google Distance Matrix API for walking distances
        if destinations:
            dist_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            dist_params = {
                'origins': f"{user_lat},{user_lng}",
                'destinations': "|".join(destinations),
                'mode': 'walking',
                'units': 'metric',
                'key': google_api_key
            }
            try:
                dm_resp = requests.get(dist_url, params=dist_params); dm_data = dm_resp.json()
            except Exception as e:
                dm_data = {}
            if dm_data.get('status') == 'OK':
                elements = dm_data.get('rows', [{}])[0].get('elements', [])
                for idx, elem in enumerate(elements):
                    if idx < len(processed_places) and elem.get('status') == 'OK':
                        dist_m = elem['distance']['value']
                        dur_s = elem['duration']['value']
                        processed_places[idx]['distance_m'] = dist_m
                        processed_places[idx]['walking_time_min'] = int(dur_s // 60)

        # Use Gemini AI for descriptions and best selection (simulated if no real API)
        gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)
        best_index = 0
        highest_rating = -1
        for idx, place in enumerate(processed_places):
            # Determine best by highest rating (as a placeholder for AI logic)
            if place['rating'] and place['rating'] > highest_rating:
                highest_rating = place['rating']; best_index = idx
            # Generate a simple description and review summary for now
            if place['name']:
                place['description'] = (
                    f"{place['name']} is a recommended place for {query}. "
                    f"It has a rating of {place['rating']} based on {place['user_ratings_count']} reviews."
                )
                if place['rating'] and place['rating'] >= 4.5:
                    place['review_summary'] = "Users give it outstanding reviews, praising its quality and experience."
                elif place['rating'] and place['rating'] >= 4.0:
                    place['review_summary'] = "Users give it very good reviews overall, with most customers being satisfied."
                elif place['rating'] and place['rating'] >= 3.0:
                    place['review_summary'] = "Reviews are mixed, with both positive feedback and some criticisms."
                else:
                    place['review_summary'] = "This place has below-average reviews from customers."
            else:
                place['description'] = "Details are unavailable for this place."
                place['review_summary'] = ""
        # Mark the best place
        if 0 <= best_index < len(processed_places):
            processed_places[best_index]['is_best'] = True

        # Save search and places to the database
        search_record = SearchHistory.objects.create(
            query=query, latitude=user_lat, longitude=user_lng, search_time=timezone.now()
        )
        place_objects = []
        for place in processed_places:
            place_obj = RecommendedPlace(
                search=search_record,
                name=place['name'],
                address=place['address'],
                rating=place.get('rating'),
                user_ratings_count=place.get('user_ratings_count') or 0,
                description=place.get('description', ''),
                review_summary=place.get('review_summary', ''),
                distance_m=place.get('distance_m'),
                walking_time_min=place.get('walking_time_min'),
                is_best=place.get('is_best', False)
            )
            place_objects.append(place_obj)
        RecommendedPlace.objects.bulk_create(place_objects)

        # Return the serialized data
        data = SearchHistorySerializer(search_record).data
        return Response(data, status=status.HTTP_200_OK)
