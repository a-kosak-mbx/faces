from typing import Any, Dict

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility


def reset(configuration: Dict[str, Any]):
    # Local configuration.
    milvus_configuration = configuration["milvus"]
    milvus_host = milvus_configuration["endpoint_url"]
    milvus_port = milvus_configuration["port"]
    milvus_collection_id = milvus_configuration["collection_id"]
    milvus_vector_size = milvus_configuration["vector_size"]

    # Setup basic connection.
    connections.connect("default", host=milvus_host, port=milvus_port)

    # Drop specified collection if exists.
    if utility.has_collection(milvus_collection_id):
        utility.drop_collection(milvus_collection_id)

    fields = [
        FieldSchema(name="face_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=128, is_primary=False),
        FieldSchema(name="path", dtype=DataType.VARCHAR, max_length=512, is_primary=False),
        FieldSchema(name="excluded", dtype=DataType.BOOL, is_primary=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=milvus_vector_size)
    ]

    schema = CollectionSchema(fields, description="Face embeddings with metadata")

    collection = Collection(name=milvus_collection_id, schema=schema)
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "IP",
        "params": {"nlist": 128}
    }

    collection.create_index("embedding", index_params)

    collection.load()
