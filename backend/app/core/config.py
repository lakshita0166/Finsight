from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# config.py lives at: KAL/backend/app/core/config.py
# .env lives at:      KAL/backend/.env
# So go 3 levels up from this file's directory: core → app → backend
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FinSight"
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    # FastAPI async DB (SQLAlchemy + asyncpg)
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Setu AA
    SETU_CLIENT_ID: str = ""
    SETU_CLIENT_SECRET: str = ""
    SETU_PRODUCT_INSTANCE_ID: str = ""
    SETU_BASE_URL: str = "https://fiu-sandbox.setu.co"
    SETU_TOKEN_URL: str = "https://uat.setu.co/api/v2/auth/token"

    # PostgreSQL — psycopg2 used by db_config.py for FI data storage
    # Must match the credentials in DATABASE_URL above
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "finsight"
    DB_USER: str = "postgre"
    DB_PASSWORD: str = "postgres"

    # RAG / Chatbot API Keys (add these lines)
    GROQ_API_KEY: str
    PINECONE_API_KEY: str

    class Config:
        env_file = str(_ENV_PATH)
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()