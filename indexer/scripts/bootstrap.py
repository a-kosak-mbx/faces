import io
from pathlib import Path
from typing import Any, Dict

import boto3
import numpy as np
import yaml
from PIL import Image
from insightface.app import FaceAnalysis
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

data_directory = Path(__file__).parent / "data"


def reset_db(configuration: Dict[str, Any]):
    milvus_configuration = configuration["milvus"]
    milvus_host = milvus_configuration["endpoint_url"]
    milvus_port = milvus_configuration["port"]
    milvus_collection_id = milvus_configuration["collection_id"]

    connections.connect("default", host=milvus_host, port=milvus_port)

    if utility.has_collection(milvus_collection_id):
        utility.drop_collection(milvus_collection_id)

    fields = [
        FieldSchema(name="item_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=200, is_primary=False),
        FieldSchema(name="face_id", dtype=DataType.INT64, is_primary=False),
        FieldSchema(name="file_searchable", dtype=DataType.BOOL),
        FieldSchema(name="face_searchable", dtype=DataType.BOOL),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=512)
    ]

    schema = CollectionSchema(fields, description="Face embeddings with metadata")

    collection = Collection(name=milvus_collection_id, schema=schema)
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }

    collection.create_index("embedding", index_params)

    collection.load()


def index_s3(configuration: Dict[str, Any]):
    # Fetch S3 configuration.
    s3_configuration = configuration["s3"]
    bucket_id = s3_configuration["bucket_id"]

    # Setup client.
    s3_client = boto3.client(
        "s3",
        endpoint_url=s3_configuration["endpoint_url"],
        aws_access_key_id=s3_configuration["access_key"],
        aws_secret_access_key=s3_configuration["secret_key"],
        region_name=s3_configuration.get("region", "us-east-1")
    )

    existing_buckets = [bucket["Name"] for bucket in s3_client.list_buckets()["Buckets"]]
    if bucket_id in existing_buckets:
        objects = s3_client.list_objects_v2(Bucket=bucket_id)
        if "Contents" in objects:
            for obj in objects["Contents"]:
                s3_client.delete_object(Bucket=bucket_id, Key=obj["Key"])
        s3_client.delete_bucket(Bucket=bucket_id)

    s3_client.create_bucket(Bucket=bucket_id)

    for file_path in data_directory.iterdir():
        if file_path.is_file():
            s3_client.upload_file(file_path.resolve(), bucket_id, file_path.name)

    # Read images.
    objects = s3_client.list_objects_v2(Bucket=bucket_id).get("Contents", [])

    app = FaceAnalysis(allowed_modules=['detection', 'recognition'], rec_model='buffalo_l')
    app.prepare(ctx_id=-1, det_size=(1024, 1024))

    milvus_configuration = configuration["milvus"]
    milvus_host = milvus_configuration["endpoint_url"]
    milvus_port = milvus_configuration["port"]
    milvus_collection_id = milvus_configuration["collection_id"]

    connections.connect("default", host=milvus_host, port=milvus_port)

    fields = [
        FieldSchema(name="item_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=200, is_primary=False),
        FieldSchema(name="face_id", dtype=DataType.INT64, is_primary=False),
        FieldSchema(name="file_searchable", dtype=DataType.BOOL),
        FieldSchema(name="face_searchable", dtype=DataType.BOOL),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=512)
    ]

    schema = CollectionSchema(fields, description="Face embeddings with metadata")

    collection = Collection(name=milvus_collection_id, schema=schema)

    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    for obj in objects:
        print(obj)
        print("------------------------------")
        image_data = s3_client.get_object(Bucket=bucket_id, Key=obj["Key"])["Body"].read()
        image = Image.open(io.BytesIO(image_data))

        faces = app.get(np.array(image))

        # for i, face in enumerate(faces):
        #    embedding = face.embedding  # это numpy-массив с вектором признаков
        #    print(f"Face {i}: embedding shape = {embedding.shape}")
        #    print(embedding)  # сам вектор
        print(faces)
        print("------------------------------")
        print("")
        print("")

        for face in faces:
            data = [
                [obj["Key"]],
                [-1],
                [True],
                [True],
                [face["embedding"]]
            ]

            collection.insert(data)
            collection.flush()


def main():
    # Read configuration file.
    configuration = {}
    with open("config.yml", "r", encoding="utf-8") as f:
        configuration = yaml.safe_load(f)

    if configuration:
        # Reset database.
        reset_db(configuration)
        index_s3(configuration)


if __name__ == "__main__":
    main()
