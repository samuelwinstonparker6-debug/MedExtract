import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True)

    PROJECT_NAME: str = 'MedExtract V2'
    VERSION: str = '2.0.0'

    # Database — SQLite for local dev; set POSTGRESQL URL in production
    DATABASE_URL: str = 'sqlite:///./medextract.db'

    # Redis / Celery
    REDIS_URL: str = 'redis://localhost:6379/0'

    # Security — MUST be overridden in production via environment variable
    API_KEY: str = 'dev-insecure-key-change-in-production'

    # CORS — explicit list; wildcard is never used with credentials
    CORS_ORIGINS: list[str] = [
        'http://localhost:5173',
        'http://localhost:3000',
        'http://localhost:80',
    ]

    # File upload
    UPLOAD_DIR: str = 'app/uploads'
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_CONTENT_TYPES: list[str] = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/jfif',
    ]

    # Fraud detection thresholds
    FRAUD_AMBER_THRESHOLD: float = 0.75
    FRAUD_RED_THRESHOLD: float = 0.88

    # Tesseract path (Windows local dev only)
    TESSERACT_CMD: str = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


settings = Settings()

# Ensure upload directory exists at startup
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
