import os
from pydantic_settings import BaseSettings


def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


class Settings(BaseSettings):
    environment: str = get_env("ENVIRONMENT", "development")
    database_url: str = get_env("DATABASE_URL", "sqlite:///./homeservice.db")
    claude_api_key: str = get_env("CLAUDE_API_KEY", "")
    claude_base_url: str = get_env("CLAUDE_BASE_URL", "https://api.anthropic.com/v1/")
    claude_model_name: str = get_env("CLAUDE_MODEL_NAME", "claude-opus-4-1-20250805")
    default_model_name: str = get_env("DEFAULT_MODEL_NAME", "claude-opus")
    api_secret_key: str = get_env("API_SECRET_KEY", "localdevsecret")
    admin_username: str = get_env("ADMIN_USERNAME", "admin")
    admin_password: str = get_env("ADMIN_PASSWORD", "password123")


settings = Settings()
