from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, settings
from app.core.index import Index


async def get_settings() -> Settings:
    return settings


SettingsDependency = Annotated[Settings, Depends(get_settings)]


async def get_index(s: Settings = Depends(get_settings)) -> Index:
    return Index(s.MILVUS_HOST, s.MILVUS_PORT, s.MILVUS_COLLECTION_ID)


IndexDependency = Annotated[Index, Depends(get_index)]
