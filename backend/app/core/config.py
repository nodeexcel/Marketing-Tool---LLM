"""Application settings loaded from environment variables via pydantic-settings."""

import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env so local development picks up values without exporting them.
load_dotenv(override=True)


class Settings(BaseSettings):
    """Central configuration — every env var the app needs."""

    # Server
    port: int = Field(8002, env="PORT")
    environment: str = Field("development", env="ENVIRONMENT")
    secret_key: str = Field("change-me-in-production-min-32-chars", env="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    @property
    def algorithm(self) -> str:
        """Alias for jwt_algorithm — used by security.py."""
        return self.jwt_algorithm

    # MongoDB
    mongodb_uri: str = Field("mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_db_name: str = Field("marketing_ai_studio", env="MONGODB_DB_NAME")

    # SQLite (legacy / fallback)
    database_url: str = Field("sqlite+aiosqlite:///./marketing.db", env="DATABASE_URL")

    # Anthropic Claude (text generation — replaces Gemini)
    anthropic_api_key: str = Field("", env="ANTHROPIC_API_KEY")

    # Black Forest Labs (Flux) — image generation (replaces Imagen)
    flux_api_key: str = Field("", env="FLUX_API_KEY")

    # Google AI — used for Veo video generation via the Gemini API path.
    # GOOGLE_API_KEY is the key Blake provided; gemini_api_key is the legacy
    # alias still read by some older code paths.
    google_api_key: str = Field("", env="GOOGLE_API_KEY")
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")
    google_cloud_project: str = Field("", env="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field("us-central1", env="GOOGLE_CLOUD_LOCATION")

    # Google Cloud Storage
    gcs_bucket_name: str = Field("marketing-ai-studio-assets", env="GCS_BUCKET_NAME")
    gcs_project_id: str = Field("", env="GCS_PROJECT_ID")
    google_application_credentials: str = Field(
        "", env="GOOGLE_APPLICATION_CREDENTIALS"
    )
    # If true, upload objects as public and return permanent URLs
    gcs_public_read: bool = Field(False, env="GCS_PUBLIC_READ")

    # Public backend URL for local asset fallback.
    backend_public_url: str = Field("http://localhost:8002", env="BACKEND_PUBLIC_URL")

    # ── Model tiers (overridable) ───────────────────────────────────────────────
    # Text generation now uses Anthropic Claude (Phase 2 swap).
    # Override via MODEL_TEXT env var — e.g. claude-sonnet-4-6 for cheaper runs.
    model_text: str = Field("claude-opus-4-7", env="MODEL_TEXT")
    # Image generation uses BFL Flux (Phase 2c). Other usable models:
    # flux-pro-1.1-ultra, flux-pro, flux-dev, flux-schnell.
    model_image_gen: str = Field("flux-pro-1.1", env="MODEL_IMAGE_GEN")
    model_video_gen: str = Field("veo-3.1-fast-generate-preview", env="MODEL_VIDEO_GEN")

    # Analytics
    analytics_enabled: bool = Field(True, env="ANALYTICS_ENABLED")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def backend_url(self) -> str:
        """Public base URL for backend-hosted assets."""
        return self.backend_public_url.rstrip("/")


settings = Settings()

# Ensure these are in os.environ for google-genai / ADK SDK
if settings.gemini_api_key:
    os.environ.setdefault("GOOGLE_API_KEY", settings.gemini_api_key)
    os.environ.setdefault("GEMINI_API_KEY", settings.gemini_api_key)
if settings.google_cloud_project:
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.google_cloud_project)
if settings.google_cloud_location:
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", settings.google_cloud_location)
if settings.google_application_credentials:
    os.environ.setdefault(
        "GOOGLE_APPLICATION_CREDENTIALS", settings.google_application_credentials
    )
