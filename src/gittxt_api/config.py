from pydantic import BaseSettings

class Settings(BaseSettings):
    api_name: str = "Gittxt API"

settings = Settings()
