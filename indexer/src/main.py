from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import io, uuid, numpy as np
from PIL import Image
from insightface.app import FaceAnalysis
import yaml


import boto3
import numpy as np
import yaml
from PIL import Image
from insightface.app import FaceAnalysis
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

API_KEY_ENV = "..."  # via env

app = FastAPI()

# prepare face analysis (device configurable)
#fa = FaceAnalysis(allowed_modules=['detection','recognition'])
#fa.prepare(ctx_id=0, det_size=(640,640))  # ctx_id should be configurable (GPU=0, CPU=-1)



@app.get("/ping/")
async def ping():
    return ""

#@app.get()



@app.post("/detect_faces/")
async def detect_faces(file: UploadFile = File(...), x_api_key: str = Header(None)):
    if x_api_key != app.state.API_KEY:
        raise HTTPException(401, "unauthorized")
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(400, "invalid_image_format")
    img_np = np.asarray(img)
    faces = fa.get(img_np)
    res = []
    for f in faces:
        face_id = str(uuid.uuid4())
        bbox = [int(f.bbox[0]), int(f.bbox[1]), int(f.bbox[2]), int(f.bbox[3])]
        res.append({"face_id": face_id, "bbox": bbox})
    if not res:
        raise HTTPException(400, "no_faces_detected")
    if len(res) > 1:
        # ТЗ: "too_many_faces" на фото более одного лица
        raise HTTPException(400, "too_many_faces")
    return res


@app.post("/search/")
async def search(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only jpg/jpeg/png files are allowed")

    content = await file.read()
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read image")

    image_array = np.array(image)

    fa = FaceAnalysis(allowed_modules=['detection', 'recognition'], rec_model='buffalo_l')
    fa.prepare(ctx_id=-1, det_size=(1024, 1024))

    faces = fa.get(image_array)

    configuration = {}
    with open("../config.yml", "r", encoding="utf-8") as f:
        configuration = yaml.safe_load(f)

    milvus_configuration = configuration["milvus"]
    milvus_host = milvus_configuration["endpoint_url"]
    milvus_port = milvus_configuration["port"]
    milvus_collection_id = milvus_configuration["collection_id"]

    connections.connect("default", host=milvus_host, port=milvus_port)
    collection = Collection(name=milvus_collection_id)

    # параметры поиска
    search_params = {
        "metric_type": "L2",  # или "IP" (inner product), или "COSINE"
        "params": {"nprobe": 10}
    }

    # выполняем поиск
    results = collection.search(
        data=[faces[0]["embedding"]],
        anns_field="embedding",
        param=search_params,
        limit=10,
        output_fields=["file_id"]
    )

    return results
    '''JSONResponse(content={
        "filename": file.filename,
        "size_bytes": len(content),
        "shape": image_array.shape,
        "dtype": str(image_array.dtype),
        "message": "Image received and converted to numpy array"
    })'''