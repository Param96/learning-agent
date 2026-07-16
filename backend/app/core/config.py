from pydantic_settings import BaseSettings
from functools import lru_cache


import os

class Settings(BaseSettings):
    APP_NAME: str = "Learning Agent"
    DEBUG: bool = False
    
    # Use /tmp for SQLite on Vercel since the rest of the filesystem is read-only
    DATABASE_URL: str = "sqlite:////tmp/learning_agent.db" if os.environ.get("VERCEL") else "sqlite:///./learning_agent.db"
    
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    NUDGE_INACTIVITY_DAYS: int = 3
    QUIZ_FAILURE_THRESHOLD: float = 0.60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()