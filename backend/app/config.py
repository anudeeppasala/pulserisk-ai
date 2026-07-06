"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PulseRisk AI"
    database_url: str = "sqlite:///./pulserisk.db"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
