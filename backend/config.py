"""
Configuration settings for the Face Recognition API
"""
import os
from pathlib import Path
from pydantic import BaseSettings

# Get base directory
BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./face_recognition.db"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Upload settings
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE: int = 50_000_000  # 50MB
    ALLOWED_EXTENSIONS: list = ["jpg", "jpeg", "png", "gif"]
    
    # Face Recognition
    FACE_RECOGNITION_MODEL: str = "Facenet512"
    SIMILARITY_THRESHOLD: float = 0.6
    MIN_FACE_SIZE: int = 20  # Minimum face size in pixels
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


# Create global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
