from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SkillLens Verification Platform"
    api_prefix: str = "/api"
    frontend_origin: str = "http://localhost:5173"
    github_token: str | None = None
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    github_api_base: str = "https://api.github.com"
    leetcode_graphql_url: str = "https://leetcode.com/graphql"
    codeforces_api_base: str = "https://codeforces.com/api"
    max_resume_bytes: int = 5 * 1024 * 1024
    api_rate_limit_capacity: int = 120
    api_rate_limit_refill_per_minute: int = 60
    external_timeout_seconds: float = 18.0

    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
