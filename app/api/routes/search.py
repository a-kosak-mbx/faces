import io
from typing import List, Optional

from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi import status

from app.api.dependencies import IndexDependency, SettingsDependency
from app.api.tools import detect_faces as tools_detect_faces
from app.core.face_item import FaceItem

router = APIRouter()


@router.post("/search", status_code=status.HTTP_200_OK)
async def search(settings: SettingsDependency, index: IndexDependency, collection_id: Optional[str] = None,
                 page: Optional[int] = 0, limit: Optional[int] = 100, file: UploadFile = File(...)) -> \
        List[FaceItem]:
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(status_code=400, detail="Only jpg/jpeg/png/webp files are allowed")

    max_image_size = settings.service.max_image_size
    if file.size / (1024 * 1024) > max_image_size:
        raise HTTPException(status_code=400, detail=f"Files greater than {max_image_size}MB are not allowed")

    file_content = await file.read()
    image = Image.open(io.BytesIO(file_content))

    detected_faces = tools_detect_faces(image)
    num_faces_detected = len(detected_faces)
    if num_faces_detected == 0:
        raise HTTPException(status_code=400, detail="No faces were detected on the image")

    if num_faces_detected > 1:
        raise HTTPException(status_code=400, detail="Two many faces on the image")

    face_items = await index.search(detected_faces[0]["embedding"], settings.service.min_absolute_score,
                                    settings.service.max_relative_score, settings.service.max_top_distance,
                                    collection_id=collection_id, page=page, page_size=settings.service.page_size,
                                    limit=limit)

    return face_items
