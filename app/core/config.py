import os
from typing import Callable

from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pydantic_settings_yaml.base_settings import YamlConfigSettingsSource


class S3Settings(BaseModel):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_id: str


class MilvusSettings(BaseModel):
    endpoint_url: str
    port: int
    collection_id: str
    vector_size: int
    login: str
    password: str


class ServiceSettings(BaseModel):
    max_image_size: int
    page_size: int
    min_absolute_score: float
    max_relative_score: float
    max_top_distance: float


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

    s3: S3Settings
    milvus: MilvusSettings
    service: ServiceSettings

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
