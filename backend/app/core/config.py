import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kollamo.ai Backend API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    YOUTUBE_API_KEY: str = ""
    MODEL_PATH: str = "google/muril-base-cased"
    DEVICE: str = "cpu"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()