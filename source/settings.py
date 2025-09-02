from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment variables
    domain: str
    rate_limit_requests: int
    rate_limit_window_seconds: int
    database_url: str

    # Custom settings
    max_code_generation_attempts: int = 10
    infinite_lifetime: int = 1_000_000


settings = Settings()
