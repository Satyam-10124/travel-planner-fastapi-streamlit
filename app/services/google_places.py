import httpx
from typing import List, Dict, Optional
from ..core.config import settings

class GooglePlacesService:
    def __init__(self):
        self.api_key = settings.google_places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    async def search_places(self, city: str, place_type: str = None, radius: int = 50000) -> List[Dict]:
        """Search for places in a city using Google Places API"""
        if not self.api_key:
            return []
        
        # First get city coordinates
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            "address": city,
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Get city coordinates
                geocode_response = await client.get(geocode_url, params=geocode_params)
                geocode_data = geocode_response.json()
                
                if not geocode_data.get("results"):
                    return []
                
                location = geocode_data["results"][0]["geometry"]["location"]
                lat, lng = location["lat"], location["lng"]
                
                # Search for places
                search_url = f"{self.base_url}/nearbysearch/json"
                search_params = {
                    "location": f"{lat},{lng}",
                    "radius": radius,
                    "key": self.api_key
                }
                
                if place_type:
                    type_mapping = {
                        "sights": "tourist_attraction",
                        "museum": "museum",
                        "food": "restaurant",
                        "nature": "park",
                        "shopping": "shopping_mall",
                        "nightlife": "night_club"
                    }
                    search_params["type"] = type_mapping.get(place_type, "tourist_attraction")
                
                search_response = await client.get(search_url, params=search_params)
                search_data = search_response.json()
                
                places = []
                for result in search_data.get("results", [])[:20]:  # Limit to 20 results
                    place = {
                        "city": city,
                        "name": result.get("name", ""),
                        "category": self._map_google_type_to_category(result.get("types", [])),
                        "lat": result["geometry"]["location"]["lat"],
                        "lng": result["geometry"]["location"]["lng"],
                        "rating": result.get("rating", 4.0),
                        "price_level": result.get("price_level", 2),
                        "description": result.get("vicinity", "")
                    }
                    places.append(place)
                
                return places
                
            except Exception as e:
                print(f"Error fetching places: {e}")
                return []
    
    def _map_google_type_to_category(self, types: List[str]) -> str:
        """Map Google Place types to our categories"""
        type_mapping = {
            "tourist_attraction": "sights",
            "museum": "museum",
            "restaurant": "food",
            "food": "food",
            "park": "nature",
            "shopping_mall": "shopping",
            "store": "shopping",
            "night_club": "nightlife",
            "bar": "nightlife"
        }
        
        for google_type in types:
            if google_type in type_mapping:
                return type_mapping[google_type]
        
        return "activity"  # Default category

google_places_service = GooglePlacesService()
