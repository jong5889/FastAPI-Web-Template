from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(".env")

class Settings(BaseSettings):
    SECRET_KEY: str = "change_this_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./test.db"
    GOOGLE_CLIENT_ID: str = "your_google_client_id.apps.googleusercontent.com"
    CSRF_SECRET_KEY: str = "another_super_secret_key_for_csrf"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
