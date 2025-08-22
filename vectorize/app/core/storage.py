from io import BytesIO
from typing import Any, Dict, Optional
from uuid import uuid4

from aioboto3 import Session

from app.api.dependencies import Settings


class Storage:
    session: Optional[Session] = None
    __endpoint_url: str
    __access_key: str
    __secret_key: str
    __bucket_id: str

    def __init__(self, settings: Settings):
        self.__endpoint_url = settings.s3.endpoint_url
        self.__access_key = settings.s3.access_key
        self.__secret_key = settings.s3.secret_key
        self.__bucket_id = settings.s3.bucket_id
        if Storage.session is None:
            Storage.session = Session()

    async def upload_file(self, data: BytesIO) -> str:
        # Generate UID for the file key.
        uid: str = str(uuid4())

        async with Storage.session.client(
                "s3",
                endpoint_url=self.__endpoint_url,
                aws_access_key_id=self.__access_key,
                aws_secret_access_key=self.__secret_key,
                region_name="us-east-1"
        ) as s3_client:
            await s3_client.put_object(Bucket=self.__bucket_id, Key=uid, Body=data)

        return uid
