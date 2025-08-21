from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.dependencies import IndexDependency, SettingsDependency, StorageDependency
from app.api.tools import detect_faces

router = APIRouter()
from typing import List, Optional, Tuple
from pydantic import BaseModel
from PIL import Image


class FaceItem(BaseModel):
    face_id: int
    photo_id: str
    path: Optional[str] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
    embedding: Optional[List[float]] = None
    excluded: bool


@router.get("/embed_status/")
async def embed_status(index: IndexDependency) -> List[FaceItem]:
    result = [
        FaceItem(
            face_id=item["face_id"],
            photo_id=item["photo_id"],
            path=item["path"],
            excluded=item["excluded"]
        ) for item in index.query_all()
    ]

    return result


@router.post("/detect_faces/", status_code=status.HTTP_200_OK)
async def detect_faces(settings: SettingsDependency, index: IndexDependency, storage: StorageDependency,
                       file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(status_code=400, detail="Only jpg/jpeg/png/webp files are allowed")

    max_image_size = settings["service"]["max_file_size"]
    if file.size / (1024 * 1024) > max_image_size:
        raise HTTPException(status_code=400, detail=f"Files greater than {max_image_size}MB are not allowed")

    file_content = await file.read()
    image = Image.open(file_content)

    detected_faces = detect_faces(image)
    if not detected_faces:
        raise HTTPException(status_code=400, detail="No faces were detected on the image")

    # Update storage with meta.
    file_id = await storage.upload_file(file_content)
    await index.insert(file_id, detected_faces)


@router.put("/add_face/")
async def add_face(face_id: int):
    raise HTTPException(status_code=501)


@router.delete("/remove/{photo_id}", status_code=status.HTTP_200_OK)
async def remove_photo(photo_id: int, index: IndexDependency):
    await index.exclude(photo_id)


@router.delete("/remove_all/", status_code=status.HTTP_200_OK)
async def remove_all(index: IndexDependency):
    await index.exclude()
