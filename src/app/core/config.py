"""Configuration settings for the Ifinder API application.
This module uses Pydantic to define and validate application settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for Ifinder API."""

    # --- App basics ---
    app_name: str = "Ifinder API"
    debug: bool = True

    # --- Database ---
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")

    # --- CLIP model ---
    clip_model_id: str = "openai/clip-vit-base-patch32"
    device: str = "cpu"  # "auto" | "cpu" | "cuda" | "mps"
    dtype: str = "float16"  # "float32" | "float16"
    batch_size: int = 32

    # --- Ingestion ---
    data_dir: str = Field(default="/data", alias="DATA_DIR")
    images_dir: str = Field(default="/data/images", alias="IMAGES_DIR")

    class Config:
        """Configuration for Pydantic settings."""

        env_file = ".env"  # auto-load variables from .env
        case_sensitive = False  # allow case-insensitive env vars


# Global settings instance
settings = Settings()
