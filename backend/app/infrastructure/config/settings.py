"""
ProspecIA - Application Settings

Configuration management following Single Responsibility Principle.
Uses Pydantic Settings for type-safe configuration from environment variables.
"""

from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Follows Open/Closed Principle - extend by adding new fields,
    don't modify existing ones.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "ProspecIA"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]
    CORS_CREDENTIALS: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list regardless of env format."""
        v = self.CORS_ORIGINS
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if not v.strip():
                return ["http://localhost:3000"]
            return [origin.strip() for origin in v.split(",")]
        return ["http://localhost:3000"]

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "prospecai"
    POSTGRES_USER: str = "prospecai_user"
    POSTGRES_PASSWORD: str = "dev_postgres_pass"
    POSTGRES_SCHEMA: str = "public"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Neo4j
    NEO4J_HOST: str = "localhost"
    NEO4J_PORT: int = 7687
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"
    NEO4J_DATABASE: str = "neo4j"

    @property
    def neo4j_uri(self) -> str:
        """Construct Neo4j connection URI."""
        return f"bolt://{self.NEO4J_HOST}:{self.NEO4J_PORT}"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_AUDIT: str = "audit-logs"
    KAFKA_TOPIC_LGPD: str = "lgpd-decisions"
    KAFKA_TOPIC_NOTIFICATIONS: str = "notifications"
    KAFKA_GROUP_ID: str = "prospecai-consumer"

    # Keycloak
    KEYCLOAK_HOST: str = "localhost"
    KEYCLOAK_PORT: int = 8080
    KEYCLOAK_REALM: str = "prospecai"
    KEYCLOAK_CLIENT_ID: str = "prospecai-backend"
    KEYCLOAK_CLIENT_SECRET: str = "secret"

    @property
    def keycloak_url(self) -> str:
        """Construct Keycloak server URL."""
        return f"http://{self.KEYCLOAK_HOST}:{self.KEYCLOAK_PORT}"

    # JWT
    JWT_SECRET_KEY: str = "change_me_jwt_secret_key_min_32_characters_long"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    JWT_REFRESH_EXPIRATION_DAYS: int = 7

    # MinIO
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "prospecai-storage"

    @property
    def minio_endpoint(self) -> str:
        """Construct MinIO endpoint."""
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"

    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # Security & Encryption
    ENCRYPTION_KEY: str = "0123456789abcdef" * 4  # 64 hex chars for AES-256
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    PASSWORD_HASH_ROUNDS: int = 12

    # Feature Flags
    FEATURE_AI_SUGGESTIONS: bool = True
    FEATURE_JWT_REQUIRED: bool = False
    FEATURE_RLS_ENABLED: bool = False
    FEATURE_AUDIT_LOGGING: bool = True
    FEATURE_LGPD_AGENT: bool = True
    FEATURE_USE_MODEL_V2_MATCHING: bool = False
    FEATURE_AB_TEST_PERCENTAGE: int = 10

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: List[str] = ["csv", "json", "pdf", "xlsx"]

    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return [ft.strip() for ft in v.split(",")]
        return v

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "/var/log/prospecai/app.log"

    # Monitoring
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    METRICS_ENABLED: bool = True

    # External APIs
    RECEITA_FEDERAL_API_URL: str = "https://www.receitaws.com.br/v1"

    # Multi-Tenancy
    DEFAULT_TENANT_ID: str = "nacional"
    TENANT_ISOLATION_ENABLED: bool = False

    # Data Retention
    AUDIT_LOG_RETENTION_YEARS: int = 5
    TEMP_FILE_RETENTION_HOURS: int = 24


# Singleton pattern for settings
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get application settings singleton.

    Implements Singleton pattern to ensure configuration is loaded once.

    Returns:
        Settings: Application settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
