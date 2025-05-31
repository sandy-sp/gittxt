from pydantic import BaseSettings, Field
from typing import List

class Settings(BaseSettings):
    # Environment (e.g., 'dev', 'prod')
    ENV: str = Field(default="prod")

    # CORS
    FRONTEND_ORIGINS: str = Field(
        default="https://www.sandy-sp.info/gittxt,http://localhost:5173"
    )

    # AWS S3
    S3_BUCKET: str = Field(..., env="GITTXT_S3_BUCKET")
    S3_REGION: str = Field(default="us-east-1")

    # Optional temp directory for file outputs
    TEMP_DIR: str = "/tmp"

    # Rate limiting config
    RATE_LIMIT: str = Field(default="30/minute")

    class Config:
        env_file = ".env"  # Optional, useful for local testing or CI

# Singleton instance
settings = Settings()
