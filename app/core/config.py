from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "Travel Planner API"
    default_city: str = "Paris"
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    google_places_api_key: str = ""
    openweather_api_key: str = ""
    frontend_url: str = "http://localhost:8501"

settings = Settings()
