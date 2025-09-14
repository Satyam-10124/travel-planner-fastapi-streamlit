import httpx
from typing import Dict, Optional
from datetime import datetime
from ..core.config import settings

class WeatherService:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, city: str) -> Optional[Dict]:
        """Get current weather for a city"""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                data = response.json()
                
                if response.status_code == 200:
                    return {
                        "city": city,
                        "temperature": data["main"]["temp"],
                        "description": data["weather"][0]["description"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": data["wind"]["speed"],
                        "icon": data["weather"][0]["icon"]
                    }
                return None
            except Exception as e:
                print(f"Error fetching weather: {e}")
                return None
    
    async def get_forecast(self, city: str, days: int = 5) -> Optional[Dict]:
        """Get weather forecast for a city"""
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                data = response.json()
                
                if response.status_code == 200:
                    forecasts = []
                    for item in data["list"]:
                        forecasts.append({
                            "datetime": datetime.fromtimestamp(item["dt"]),
                            "temperature": item["main"]["temp"],
                            "description": item["weather"][0]["description"],
                            "humidity": item["main"]["humidity"],
                            "wind_speed": item["wind"]["speed"],
                            "icon": item["weather"][0]["icon"]
                        })
                    
                    return {
                        "city": city,
                        "forecasts": forecasts
                    }
                return None
            except Exception as e:
                print(f"Error fetching forecast: {e}")
                return None

weather_service = WeatherService()
