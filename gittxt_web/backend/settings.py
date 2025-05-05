from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_ORIGINS: str = ""  # Comma-separated list of allowed origins

settings = Settings()
