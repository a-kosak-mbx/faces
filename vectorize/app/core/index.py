from typing import Any, Dict, List, Optional

import numpy as np
from pymilvus import AsyncMilvusClient


class Index:
    __collection_id: str
    __client: AsyncMilvusClient

    def __init__(self, host: str, port: int, login: str, password: str, collection_id: str):
        self.__collection_id = collection_id
        self.__client = AsyncMilvusClient(uri=f"http://{host}:{port}", token=f"{login}:{password}")

    async def query(self, embedding: np.ndarray, limit: int):
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }

        results = await self.__client.search(
            collection_name=self.__collection_id,
            data=[embedding, ],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=["file_id", "face_id"]
        )

        return results

    async def query_all(self) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = await self.__client.query(
            collection_name=self.__collection_id,
            filter="face_id >= 0",
            output_fields=["face_id", "photo_id", "path", "excluded", ]
        )

        return result

    async def exclude(self, photo_id: Optional[str] = None):
        condition = f"photo_id == '{photo_id}'" if photo_id else ""
        entries = await self.__client.query(
            collection_name=self.__collection_id,
            filter=condition,
            output_fields=["face_id", "file_id", "path", "bbox", "embedding", "excluded", ]
        )

        entities_to_upsert = []
        for entity in entries:
            entity["excluded"] = True
            entities_to_upsert.append(entity)

        await self.__client.insert(self.__collection_id, entities_to_upsert)

    async def insert(self, photo_id: str, detected_faces: List[Dict[str, Any]]):
        entities_to_insert = []
        for face in detected_faces:
            entity = {
                "file_id": photo_id,
                # "bbox": face["bbox"],
                "path": photo_id,
                "embedding": face["embedding"],
                "excluded": False,
            }

            entities_to_insert.append(entity)

        await self.__client.insert(self.__collection_id, entities_to_insert)
