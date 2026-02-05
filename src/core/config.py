from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/chatapp"

settings = Settings()
