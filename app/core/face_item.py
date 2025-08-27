from fastapi import APIRouter

router = APIRouter()
from typing import List, Optional, Tuple
from pydantic import BaseModel


class FaceItem(BaseModel):
    face_id: int
    photo_id: str
    collection_id: Optional[str] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
    embedding: Optional[List[float]] = None
