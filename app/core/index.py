from typing import Any, Dict, List, Optional

import numpy as np
from pymilvus import AsyncMilvusClient

from app.core.face_item import FaceItem

INDEX_FIELD_FACE_ID: str = "face_id"
INDEX_FIELD_PHOTO_ID: str = "photo_id"
INDEX_FIELD_COLLECTION_ID: str = "collection_id"
INDEX_FIELD_BBOX: str = "bbox"
INDEX_FIELD_EMBEDDING: str = "embedding"

INDEX_FIELDS: List[str] = [
    INDEX_FIELD_FACE_ID,
    INDEX_FIELD_PHOTO_ID,
    INDEX_FIELD_COLLECTION_ID,
    INDEX_FIELD_BBOX,
    INDEX_FIELD_EMBEDDING,
]


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

    async def query_all(self, collection_id: Optional[str] = None) -> List[FaceItem]:
        if collection_id:
            condition = f"{INDEX_FIELD_COLLECTION_ID} == {collection_id}"
        else:
            condition = f"{INDEX_FIELD_COLLECTION_ID} != ''"

        items = await self.__client.query(
            collection_name=self.__collection_id,
            filter=condition,
            output_fields=[INDEX_FIELD_FACE_ID, INDEX_FIELD_PHOTO_ID, ]
        )

        face_items = [
            FaceItem(
                face_id=item[INDEX_FIELD_FACE_ID],
                photo_id=item[INDEX_FIELD_PHOTO_ID],
            ) for item in items
        ]

        return face_items

    async def query_photo(self, photo_id: str) -> List[FaceItem]:
        items = await self.__client.query(
            collection_name=self.__collection_id,
            filter=f"{INDEX_FIELD_PHOTO_ID} == {photo_id}",
            output_fields=INDEX_FIELDS
        )

        face_items = [
            FaceItem(
                face_id=item[INDEX_FIELD_FACE_ID],
                photo_id=item[INDEX_FIELD_PHOTO_ID],
                collection_id=item[INDEX_FIELD_COLLECTION_ID],
                bbox=item[INDEX_FIELD_BBOX],
                embedding=item[INDEX_FIELD_EMBEDDING]
            ) for item in items
        ]

        return face_items

    async def exclude(self, photo_id: Optional[str] = None, collection_id: Optional[str] = None):
        index_condition = f"{INDEX_FIELD_PHOTO_ID} == '{photo_id}'" if photo_id else f"{INDEX_FIELD_PHOTO_ID} != ''"
        collection_condition = f"{INDEX_FIELD_COLLECTION_ID} == '{collection_id}'" if collection_id else ""
        condition = index_condition
        if collection_condition:
            condition += " and " + collection_condition

        await self.__client.delete(
            collection_name=self.__collection_id,
            filter=condition
        )

    async def insert(self, photo_id: str, collection_id: str, detected_faces: List[Dict[str, Any]]):
        entities_to_insert = []
        for face in detected_faces:
            entity = {
                INDEX_FIELD_PHOTO_ID: photo_id,
                INDEX_FIELD_COLLECTION_ID: collection_id,
                INDEX_FIELD_BBOX: face["bbox"],
                INDEX_FIELD_EMBEDDING: face["embedding"],
            }

            entities_to_insert.append(entity)

        await self.__client.insert(self.__collection_id, entities_to_insert)

    async def search(self, vector: np.ndarray, collection_id: Optional[str] = None, page: Optional[int] = None,
                     page_size: Optional[int] = None, limit: int = 100) -> List[FaceItem]:
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }

        condition = f"{INDEX_FIELD_COLLECTION_ID} == '{collection_id}'" if collection_id else ""

        faces = await self.__client.search(
            collection_name=self.__collection_id,
            data=[vector, ],
            anns_field="embedding",
            filter=condition,
            search_param=search_params,
            limit=limit,
            output_fields=INDEX_FIELDS
        )

        if page is not None and page_size is not None:
            offset = page * page_size
            size = page_size
            size = max(0, min(size, limit - offset))
        else:
            offset = 0
            size = limit

        face_items = [FaceItem(
            face_id=face["entity"]["face_id"],
            photo_id=face["entity"]["file_id"],
            collection_id=face["entity"]["path"],
            bbox=face["entity"]["bbox"],
            embedding=face["entity"]["embedding"],
        ) for face in faces[offset:offset + size]]

        return face_items
