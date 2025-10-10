from functools import lru_cache
from pathlib import Path
from typing import Literal

from langchain_mistralai import ChatMistralAI
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mistral_api_key: SecretStr | None = None
    chat_model_size: Literal["large"] | Literal["medium"] | Literal["small"] = "small"
    chat_model_temperature: float = 0.0
    database_path: str = str(
        Path(__file__).parents[2] / "data" / "atlas-assistant-docs-mistral-index"
    )

    model_config = SettingsConfigDict(env_file=".env")

    def get_chat_model(self) -> ChatMistralAI:
        return ChatMistralAI(
            model_name=f"mistral-{self.chat_model_size}-latest",  # type: ignore
            api_key=self.mistral_api_key,  # type: ignore
            temperature=self.chat_model_temperature,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
