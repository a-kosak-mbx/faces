import io

import numpy as np
from PIL import Image
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from insightface.app import FaceAnalysis
from app.api.dependencies import Index, get_index
router = APIRouter()
from typing import Optional
from pydantic import BaseModel


class FaceItem(BaseModel):
    face_id: int
    photo_id: str
    path: Optional[str] = None
    bbox: Optional[tuple[float, float, float, float]] = None
    embedding: Optional[list[float]] = None
    excluded: bool


@router.get("/embed_status/")
async def embed_status(index: Index = Depends(get_index)) -> list[FaceItem]:
    result = [
        FaceItem(
            face_id=item["face_id"],
            photo_id=item["photo_id"],
            path=item["path"],
            excluded=item["excluded"]
        ) for item in index.query_all()
    ]

    return result

