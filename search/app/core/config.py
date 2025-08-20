import os
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pydantic_settings_yaml.base_settings import YamlConfigSettingsSource


def yaml_config_settings(base_settings: BaseSettings) -> dict[str, Any]:
    config_file = Path("config.yaml")
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    return {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        yaml_file=os.environ.get("SETTINGS_YAML_FILE", "config.yml"),
        secrets_dir=os.environ.get("SETTINGS_SECRETS_DIR", "secrets"),
        extra="ignore",
    )

    # Common settings.
    PROJECT_NAME: str = "FaceDetector"
    API_V1_STR: str = "/api/v1"
    X_API_KEY: str = "default-x-api-key"
    MAX_IMAGE_SIZE: int = 5  # The size of an image file to search is 5MB max.

    # Milvus settings.
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_ID: str = "faces"

    @classmethod
    def settings_customise_sources(cls,
                                   settings_cls: type[BaseSettings],
                                   init_settings: PydanticBaseSettingsSource,
                                   env_settings: PydanticBaseSettingsSource,
                                   dotenv_settings: PydanticBaseSettingsSource,
                                   file_secret_settings: PydanticBaseSettingsSource,
                                   ) -> tuple[Callable, ...]:
        return (
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            init_settings,
            file_secret_settings
        )


settings = Settings()  # type: ignore
