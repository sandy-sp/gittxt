from pydantic import BaseSettings

class Settings(BaseSettings):
    api_name: str = "Gittxt API"
    ttl_seconds: int = 600  
    log_level: str = "info"
    output_base: str = "/tmp"  

    class Config:
        env_file = ".env"

settings = Settings()
