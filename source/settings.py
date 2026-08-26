from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment variables
    domain: str
    frontend: str
    rate_limit_requests: int
    rate_limit_window_seconds: int
    database_url: str
    cors_origins: str

    # Custom settings
    max_code_generation_attempts: int = 10

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS is a comma-separated string; split it into the list CORSMiddleware expects."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
