from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_secret: str = "change_me"
    jwt_secret: str = "change_me"
    database_url: str = "sqlite:///./calcsteam.db"
    redis_url: str = "redis://localhost:6379/0"
    encryption_key: str = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    default_timezone: str = "Europe/Moscow"
    rate_fetch_interval_minutes: int = 60
    reservation_ttl_minutes: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
