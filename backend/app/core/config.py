import os

from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "NER-LogiSense Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "ner-logisense-secure-super-key-2026-tactical-defense-command"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Database: Default to local SQLite for instant developer setup, or PostgreSQL+PostGIS in production
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ner_logisense.db")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Object Storage (S3 / MinIO)
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "ner-logisense-media")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")

    # External APIs
    IMD_WEATHER_API_KEY: str = os.getenv("IMD_WEATHER_API_KEY", "demo_imd_key")
    BHUVAN_GIS_API_KEY: str = os.getenv("BHUVAN_GIS_API_KEY", "demo_bhuvan_key")

    # Default Route Optimization Weights
    # Cost = alpha * travel_time + beta * risk_score + gamma * operating_cost
    DEFAULT_ROUTING_ALPHA: float = 0.45
    DEFAULT_ROUTING_BETA: float = 0.40
    DEFAULT_ROUTING_GAMMA: float = 0.15

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "*",
    ]


settings = Settings()
