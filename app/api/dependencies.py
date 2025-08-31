from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.openapi.models import APIKey
from fastapi.security.api_key import APIKeyHeader

from app.core.config import Settings, settings as global_settings
from app.core.index import Index
from app.core.storage import Storage


async def get_settings() -> Settings:
    return global_settings


SettingsDependency = Annotated[Settings, Depends(get_settings)]


async def get_index(settings: Settings = Depends(get_settings)) -> Index:
    return Index(settings.milvus.endpoint_url, settings.milvus.port, settings.milvus.login, settings.milvus.password,
                 settings.milvus.collection_id)


IndexDependency = Annotated[Index, Depends(get_index)]


async def get_storage(settings: SettingsDependency) -> Storage:
    return Storage(settings)


StorageDependency = Annotated[Storage, Depends(get_storage)]

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(settings: SettingsDependency, api_key: str = Security(api_key_header)):
    if api_key == settings.X_API_KEY:
        return api_key
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")


ApiKeyDependency = Annotated[APIKey, Depends(get_api_key)]
