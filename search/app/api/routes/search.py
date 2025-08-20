import io

import numpy as np
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException
from insightface.app import FaceAnalysis

router = APIRouter()


@router.post("/search/")
async def search(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(status_code=400, detail="Only jpg/jpeg/png/webp files are allowed")

    # TODO: add file size check.

    content = await file.read()
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read image")

    # Initialize model.
    # TODO: move to external dependency?
    fa = FaceAnalysis(allowed_modules=['detection', 'recognition'], rec_model='buffalo_l')
    fa.prepare(ctx_id=-1, det_size=(1024, 1024))

    image_array = np.array(image)
    faces = fa.get(image_array)

    num_faces_detected = len(faces)

    # TODO: add detailed description.
    if num_faces_detected == 0:
        raise HTTPException(status_code=400)

    if num_faces_detected > 1:
        raise HTTPException(status_code=400)

    # TODO: replace limit with the parametric value.
    face_embedding = faces[0]["embedding"]
    index.fetch(face_embedding, 10)


    milvus_configuration = configuration["milvus"]
    milvus_host = milvus_configuration["endpoint_url"]
    milvus_port = milvus_configuration["port"]
    milvus_collection_id = milvus_configuration["collection_id"]

    connections.connect("default", host=milvus_host, port=milvus_port)
    collection = Collection(name=milvus_collection_id)

    search_params = {
        "metric_type": "IP",
        "params": {"nprobe": 10}
    }

    results = collection.fetch(
        data=[faces[0]["embedding"]],
        anns_field="embedding",
        param=search_params,
        limit=10,
        output_fields=["file_id"]
    )



    return results
