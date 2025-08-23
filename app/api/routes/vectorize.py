import io

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.dependencies import IndexDependency, SettingsDependency, StorageDependency
from app.api.tools import detect_faces as tools_detect_faces

router = APIRouter()
from typing import List
from PIL import Image

from app.core.face_item import FaceItem


@router.get("/embed_status")
async def embed_status(index: IndexDependency) -> List[FaceItem]:
    items = await index.query_all()

    result = [
        FaceItem(
            face_id=item["face_id"],
            photo_id=item["file_id"],
            path=item["path"],
            excluded=item["excluded"]
        ) for item in items
    ]
    return result


@router.post("/detect_faces", status_code=status.HTTP_200_OK)
async def detect_faces(settings: SettingsDependency, index: IndexDependency, storage: StorageDependency,
                       file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(status_code=400, detail="Only jpg/jpeg/png/webp files are allowed")

    max_image_size = settings.service.max_image_size
    if file.size / (1024 * 1024) > max_image_size:
        raise HTTPException(status_code=400, detail=f"Files greater than {max_image_size}MB are not allowed")

    file_content = await file.read()
    image = Image.open(io.BytesIO(file_content))

    detected_faces = tools_detect_faces(image)
    if not detected_faces:
        raise HTTPException(status_code=400, detail="No faces were detected on the image")

    # Update storage with meta.
    file_id = await storage.upload_file(file_content)
    await index.insert(file_id, detected_faces)


@router.put("/add_face")
async def add_face(face_id: int):
    raise HTTPException(status_code=501)


@router.delete("/remove/{photo_id}", status_code=status.HTTP_200_OK)
async def remove_photo(photo_id: str, index: IndexDependency):
    await index.exclude(photo_id)


@router.delete("/remove_all/", status_code=status.HTTP_200_OK)
async def remove_all(index: IndexDependency):
    await index.exclude()
