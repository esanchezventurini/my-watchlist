from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "My Watchlist API"
    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int

    omdb_api_key: str
    omdb_base_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
