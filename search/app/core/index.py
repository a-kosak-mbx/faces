import numpy as np
from pymilvus import connections, Collection


class Index:
    __collection_id: str
    __collection: Collection

    DEFAULT_CONNECTION_ALIAS: str = "default"

    def __init__(self, host: str, port: int, collection_id: str):
        self.__collection_id = collection_id
        if not connections.has_connection(Index.DEFAULT_CONNECTION_ALIAS):
            connections.connect(alias=Index.DEFAULT_CONNECTION_ALIAS, host=host, port=port)
        self.__collection = Collection(name=collection_id)

    def fetch(self, embedding: np.ndarray, limit: int):
        search_params = {
            "metric_type": "L2",  # или "IP" (inner product), или "COSINE"
            "params": {"nprobe": 10}
        }

        results = self.__collection.search(
            data=[embedding, ],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=["file_id", "face_id"]
        )

        return results
