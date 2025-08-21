from pathlib import Path
from typing import Any, Dict

import boto3

from bootstrap.vectorize import vectorize_photo


def setup_s3_client(configuration: Dict[str, Any]):
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

    return s3_client


def reset(configuration: Dict[str, Any]):
    # Fetch S3 configuration.
    s3_configuration = configuration["s3"]
    bucket_id = s3_configuration["bucket_id"]

    s3_client = setup_s3_client(configuration)

    existing_buckets = [bucket["Name"] for bucket in s3_client.list_buckets()["Buckets"]]
    if bucket_id in existing_buckets:
        objects = s3_client.list_objects_v2(Bucket=bucket_id)
        if "Contents" in objects:
            for obj in objects["Contents"]:
                s3_client.delete_object(Bucket=bucket_id, Key=obj["Key"])
        s3_client.delete_bucket(Bucket=bucket_id)

    s3_client.create_bucket(Bucket=bucket_id)


def fill(configuration: Dict[str, Any]):
    # Process each file in directory.
    data_directory = Path(__file__).parent.parent / "data"
    for file_path in data_directory.iterdir():
        if file_path.is_file():
            # Upload photo to the vectorization service.
            vectorize_photo(configuration, file_path)
