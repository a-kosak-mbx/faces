from typing import Any, Dict, List, Optional

import numpy as np
from pymilvus import AsyncMilvusClient

from app.core.face_item import FaceItem


class Index:
    __collection_id: str
    __client: AsyncMilvusClient
    __host: str
    __port: int
    __login: str
    __password: str

    def __init__(self, host: str, port: int, login: str, password: str, collection_id: str):
        self.__host = host
        self.__port = port
        self.__login = login
        self.__password = password
        self.__collection_id = collection_id
        self.__client = self.__get_client()

    def __get_client(self) -> AsyncMilvusClient:
        return AsyncMilvusClient(uri=f"http://{self.__host}:{self.__port}", token=f"{self.__login}:{self.__password}")

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
        result = await self.__client.query(
            collection_name=self.__collection_id,
            filter="face_id >= 0",
            output_fields=["face_id", "file_id", "path", "excluded", ]
        )

        return result

    async def exclude(self, photo_id: Optional[str] = None):
        condition = f"file_id == '{photo_id}'" if photo_id else "file_id != ''"
        entries = await self.__client.query(
            collection_name=self.__collection_id,
            filter=condition,
            output_fields=["face_id", "file_id", "path", "embedding", "excluded", ]
        )

        face_ids = [str(entry["face_id"]) for entry in entries]

        entries_to_upsert = []
        for entry in entries:
            entry["excluded"] = True
            entries_to_upsert.append(entry)

        await self.__client.delete(
            collection_name=self.__collection_id,
            filter=f"face_id in [{', '.join(face_ids)}]"
        )

        await self.__client.upsert(self.__collection_id, entries_to_upsert)

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

    async def search(self, vector: np.ndarray, limit: int = 10) -> List[FaceItem]:
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }

        faces = await self.__client.search(
            collection_name=self.__collection_id,
            data=[vector, ],
            anns_field="embedding",
            search_param=search_params,
            limit=limit,
            output_fields=["face_id", "file_id", "path", "embedding", "excluded", ]
        )

        face_items = [FaceItem(
            face_id=face['entity']["face_id"],
            photo_id=face['entity']["file_id"],
            path=face['entity']["path"],
            embedding=face['entity']["embedding"],
            excluded=face['entity']["excluded"]
        ) for face in faces[0]]

        return face_items
