"""
Application Settings and Configuration

This module loads configuration from environment variables and provides
default values for the transcription backend application.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME: str = os.getenv("DB_NAME", "transcription_db")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Whisper Model Configuration
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "small")
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
    CHUNK_DURATION: float = float(os.getenv("CHUNK_DURATION", "2.0"))
    
    # Audio Processing
    MAX_AUDIO_BUFFER_SIZE: int = int(os.getenv("MAX_AUDIO_BUFFER_SIZE", "10"))
    MIN_CHUNKS_FOR_TRANSCRIPTION: int = int(os.getenv("MIN_CHUNKS_FOR_TRANSCRIPTION", "2"))
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = eval(os.getenv("ALLOWED_ORIGINS", '["*"]'))
    ALLOW_CREDENTIALS: bool = os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = eval(os.getenv("SUPPORTED_LANGUAGES", '["auto", "en", "yo", "ig", "ha"]'))
    
    # Computed values
    @property
    def CHUNK_SIZE(self) -> int:
        """Calculate chunk size based on sample rate and duration"""
        return int(self.SAMPLE_RATE * self.CHUNK_DURATION)
    
    @property
    def DATABASE_URL(self) -> str:
        """Get full database URL"""
        return f"{self.MONGO_URI}{self.DB_NAME}"

# Create global settings instance
settings = Settings()

# Export commonly used settings for convenience
MONGO_URI = settings.MONGO_URI
DB_NAME = settings.DB_NAME
HOST = settings.HOST
PORT = settings.PORT
DEBUG = settings.DEBUG
WHISPER_MODEL_SIZE = settings.WHISPER_MODEL_SIZE
SAMPLE_RATE = settings.SAMPLE_RATE
CHUNK_DURATION = settings.CHUNK_DURATION
CHUNK_SIZE = settings.CHUNK_SIZE
MAX_AUDIO_BUFFER_SIZE = settings.MAX_AUDIO_BUFFER_SIZE
MIN_CHUNKS_FOR_TRANSCRIPTION = settings.MIN_CHUNKS_FOR_TRANSCRIPTION
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
ALLOW_CREDENTIALS = settings.ALLOW_CREDENTIALS
LOG_LEVEL = settings.LOG_LEVEL
SUPPORTED_LANGUAGES = settings.SUPPORTED_LANGUAGES
DATABASE_URL = settings.DATABASE_URL
