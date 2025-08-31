from typing import List

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    size: List[str] = []
    image_class: List[str] = []
    misc: List[str] = []


class UploadResponse(BaseModel):
    success: List[str]
    error: ErrorResponse
