from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Research Agent Platform"
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"
    auto_create_tables: bool = True
    search_provider: str = "tavily"
    tavily_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")


settings = Settings()
