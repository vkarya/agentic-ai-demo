"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    llm_api_base: str = Field(
        default="http://localhost:11434/v1",
        validation_alias=AliasChoices("API_BASE", "LLM_API_BASE"),
    )
    llm_api_key: str = Field(
        default="ollama",
        validation_alias=AliasChoices("API_KEY", "LLM_API_KEY", "OPENAI_API_KEY"),
    )
    llm_model: str = Field(
        default="llama3.2",
        validation_alias=AliasChoices("MODEL_NAME", "LLM_MODEL"),
    )
    cors_origins: str = "http://localhost:4200"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
