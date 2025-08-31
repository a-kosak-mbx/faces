import io
import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import ApiKeyDependency, IndexDependency, SettingsDependency
from app.api.tools import detect_faces as tools_detect_faces
from app.core.image_meta import ImageMeta
from app.core.responses import UploadResponse, ErrorResponse

router = APIRouter()
from typing import Dict, List, Optional
from PIL import Image

from app.core.face_item import FaceItem


@router.get("/embed_status")
async def embed_status(index: IndexDependency, collection_id: Optional[str] = None) -> List[FaceItem]:
    items = await index.query_all(collection_id)
    return items


@router.get("/check_photo_status")
async def check_photo_status(photo_id: str, index: IndexDependency) -> List[FaceItem]:
    items = await index.query_photo(photo_id)
    return items


@router.post("/vectorize", status_code=status.HTTP_200_OK)
async def vectorize(settings: SettingsDependency, index: IndexDependency, files: List[UploadFile] = File(...),
                    meta: str = Form(...), collection_id: Optional[str] = None) -> UploadResponse:
    x = json.loads(meta)
    image_meta = [ImageMeta(**item) for item in json.loads(meta)]
    if len(image_meta) != len(files):
        raise HTTPException(status_code=400, detail="Inconsistent meta")

    uploaded_files: List[str] = []
    error: Dict[str, List[str]] = {
        "size": [],
        "image_class": [],
        "misc": [],
    }

    max_image_size = settings.service.max_image_size

    for file_index, file in enumerate(files):
        uid = image_meta[file_index].uid
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            error["image_class"].append(uid)

        if file.size / (1024 * 1024) > max_image_size:
            error["size"].append(uid)

        file_content = await file.read()
        image = Image.open(io.BytesIO(file_content))

        detected_faces = tools_detect_faces(image)
        if not detected_faces:
            error["misc"].append(uid)

        await index.insert(uid, collection_id, detected_faces)
        uploaded_files.append(uid)

    return UploadResponse(success=uploaded_files, error=ErrorResponse(**error))


@router.delete("/remove/{photo_id}", status_code=status.HTTP_200_OK)
async def remove_photo(photo_id: str, index: IndexDependency, api_key: ApiKeyDependency):
    await index.exclude(photo_id)


@router.delete("/remove_all", status_code=status.HTTP_200_OK)
async def remove_all(index: IndexDependency, collection_id: Optional[str] = None):
    await index.exclude(collection_id=collection_id)
