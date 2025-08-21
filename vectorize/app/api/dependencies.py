from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, settings as global_settings
from app.core.index import Index
from app.core.storage import Storage


async def get_settings() -> Settings:
    return global_settings


SettingsDependency = Annotated[Settings, Depends(get_settings)]


async def get_index(settings: Settings = Depends(get_settings)) -> Index:
    return Index(settings.MILVUS_HOST, settings.MILVUS_PORT, settings.MILVUS_LOGIN, settings.MILVUS_PASSWORD,
                 settings.MILVUS_COLLECTION_ID)


IndexDependency = Annotated[Index, Depends(get_index)]


async def get_storage(settings: SettingsDependency) -> Storage:
    return Storage(settings["s3"])


StorageDependency = Annotated[Storage, Depends(get_storage)]
