from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment variables
    domain: str
    database_url: str

    # Custom settings
    max_attempts: int = 10
    infinite_lifetime: int = 9999


settings = Settings()
