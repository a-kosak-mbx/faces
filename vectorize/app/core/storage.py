from io import BytesIO
from typing import Any, Dict, Optional
from uuid import uuid4

from aioboto3 import Session


class Storage:
    session: Optional[Session] = None
    __configuration: Dict[str, Any]

    def __init__(self, s3_configuration: Dict[str, Any]):
        self.__configuration = s3_configuration
        if Storage.session is None:
            Storage.session = Session()

    async def upload_file(self, data: BytesIO) -> str:
        # Generate UID for the file key.
        uid: str = str(uuid4())

        configuration = self.__configuration

        async with Storage.session.client(
                "s3",
                endpoint_url=configuration["endpoint_url"],
                aws_access_key_id=configuration["access_key"],
                aws_secret_access_key=configuration["secret_key"],
                region_name=configuration.get("region", "us-east-1")
        ) as s3_client:
            await s3_client.put_object(data, configuration["bucket_id"], uid)

        return uid
