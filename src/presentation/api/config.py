from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DATABASE: str
    LLM_PROVIDER: str = "localai"
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str
    APP_ENV: str = "development"
    APP_DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
