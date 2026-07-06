"""
Configuration settings for CropSense AI Backend
Uses Pydantic Settings for environment variable management

IMPORTANT: AWS credentials are loaded ONLY from environment variables.
Do NOT use ~/.aws/credentials file. All AWS configuration must be in .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "CropSense AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "test-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:4200,http://localhost:5173,http://127.0.0.1:3000,http://192.168.1.5:3000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,192.168.1.5"
    
    # Security Settings
    MAX_REQUEST_SIZE_MB: int = 10  # Maximum request size in MB
    MAX_JSON_FIELDS: int = 1000  # Maximum number of fields in JSON request
    MAX_STRING_LENGTH: int = 10000  # Maximum string length in requests
    MAX_ARRAY_LENGTH: int = 1000  # Maximum array length in requests
    ENABLE_CSRF_PROTECTION: bool = True  # Enable CSRF protection
    ENABLE_REQUEST_LOGGING: bool = True  # Enable request logging for security monitoring
    
    # Database - PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "cropsense_dev"
    POSTGRES_PORT: int = 5432
    
    # Database URLs
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = "your-project-id"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_REGION: str = "asia-south1"
    FIREBASE_PROJECT_ID: str = "your-firebase-project"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    CLOUD_SQL_INSTANCE: Optional[str] = None
    GOOGLE_CLOUD_SQL_INSTANCE: Optional[str] = None  # Used by database.py for Cloud SQL connector
    CLOUD_SQL_DB: str = "cropsense_gcp"
    GCS_BUCKET: str = "cropsense-uploads"
    BIGQUERY_DATASET: str = "cropsense_analytics"
    FIRESTORE_COLLECTION_PREFIX: str = "cropsense"
    
    # External APIs
    OPENWEATHER_API_KEY: str = "test-api-key"
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    DATAGOV_API_KEY: Optional[str] = None
    DATAGOV_MOISTURE_API_KEY: Optional[str] = None
    
    # SMS and Notifications
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Amazon SNS Configuration
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: str = ".jpg,.jpeg,.png,.gif,.webp"
    
    # ML Model Configuration
    ML_MODEL_PATH: str = "models/"
    VECTOR_DIMENSION: int = 384
    SIMILARITY_THRESHOLD: float = 0.7
    
    # SageMaker Configuration
    SAGEMAKER_MODEL_BUCKET: str = "cropsense-sagemaker-models"
    SAGEMAKER_EXECUTION_ROLE_ARN: Optional[str] = None
    SAGEMAKER_ENDPOINT_PREFIX: str = "cropsense"
    SAGEMAKER_ENABLED: bool = False  # Enable SageMaker endpoints (set to True when deployed)
    SAGEMAKER_YIELD_ENDPOINT: str = "cropsense-yield-prediction"
    SAGEMAKER_HARVEST_ENDPOINT: str = "cropsense-harvest-prediction"
    SAGEMAKER_QUALITY_ENDPOINT: str = "cropsense-quality-prediction"
    
    # Caching
    CACHE_ENABLED: bool = True  # Enable/disable Redis caching
    CACHE_TTL_SECONDS: int = 3600  # 1 hour default TTL
    WEATHER_CACHE_TTL: int = 21600  # 6 hours
    FARM_CACHE_TTL: int = 3600  # 1 hour
    MARKETPLACE_CACHE_TTL: int = 60  # 1 minute
    STRATEGY_CACHE_TTL: int = 7200  # 2 hours
    MARKET_DATA_CACHE_TTL: int = 86400  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True  # Enable/disable rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100  # Authenticated users
    RATE_LIMIT_PUBLIC_PER_MINUTE: int = 20  # Public/unauthenticated users
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # Time window for rate limiting
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = False
    
    # SHC WMS Configuration
    SHC_WMS_PATH: str = ""          # Obfuscated WMS path segment (required for SHC fetching)
    SHC_CYCLE: str = "2025-26"      # Default SHC survey cycle
    SHC_WMS_BASE: str = "https://soilhealth4.dac.gov.in"

    # SLUSI Ingestion Schedule
    SLUSI_INGEST_INTERVAL_DAYS: int = 7

    # Celery Configuration (for background tasks)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    def get_allowed_origins_list(self) -> List[str]:
        """Get ALLOWED_ORIGINS as a list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    def get_allowed_hosts_list(self) -> List[str]:
        """Get ALLOWED_HOSTS as a list"""
        if isinstance(self.ALLOWED_HOSTS, str):
            return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
        return self.ALLOWED_HOSTS
    
    def get_allowed_extensions_list(self) -> List[str]:
        """Get ALLOWED_IMAGE_EXTENSIONS as a list"""
        if isinstance(self.ALLOWED_IMAGE_EXTENSIONS, str):
            return [ext.strip() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",")]
        return self.ALLOWED_IMAGE_EXTENSIONS

# Create settings instance
settings = Settings()

# DynamoDB Table Names
class DynamoDBTables:
    """DynamoDB table names with prefix"""
    
    @staticmethod
    def get_table_name(base_name: str) -> str:
        return f"{settings.DYNAMODB_TABLE_PREFIX}-{base_name}"
    
    CROP_PREDICTIONS = property(lambda self: self.get_table_name("crop-predictions"))
    USER_ANALYTICS = property(lambda self: self.get_table_name("user-analytics"))
    WEATHER_CACHE = property(lambda self: self.get_table_name("weather-cache"))
    NOTIFICATIONS = property(lambda self: self.get_table_name("notifications"))
    RECOMMENDATIONS = property(lambda self: self.get_table_name("recommendations"))

dynamodb_tables = DynamoDBTables()

# Validation
def validate_settings():
    """Validate critical settings - only in production"""
    # Skip validation in test/development environments
    if settings.ENVIRONMENT in ["test", "testing", "development"]:
        return
    
    errors = []
    
    if settings.SECRET_KEY == "test-secret-key-change-in-production":
        errors.append("SECRET_KEY must be changed in production")
    
    if settings.OPENWEATHER_API_KEY == "test-api-key":
        errors.append("OPENWEATHER_API_KEY must be configured in production")
    
    if errors:
        raise ValueError(f"Production configuration errors: {', '.join(errors)}")

# Validate on import (skip if SKIP_VALIDATION is set)
if os.getenv("SKIP_VALIDATION") != "true":
    try:
        validate_settings()
    except Exception as e:
        # Log warning but don't fail in development
        if settings.ENVIRONMENT not in ["test", "testing", "development"]:
            raise


def get_system_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Resolves settings dynamically from the system_settings database table,
    falling back to environment variables and configuration defaults.
    """
    try:
        from app.orm.system_setting import SystemSetting
        setting = SystemSetting.find(key, 'key')
        if setting and setting.items:
            if setting.items.get('enable', 1) == 1:
                return setting.items.get('value')
    except Exception:
        # Fallback silently if DB is uninitialized or other issues occur
        pass

    # Fallback to environment variable
    val = os.getenv(key)
    if val is not None:
        return val

    # Fallback to pydantic config instance attributes if present
    if hasattr(settings, key):
        return getattr(settings, key)

    return default