from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="settings.env", env_file_encoding="utf-8")
    API_ID: int
    API_HASH: str

    CLICKS: list[int]
    MIN_ENERGY: int

    SLEEP_TIME: int
settings = Settings()