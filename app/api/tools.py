import io
from typing import Any, Dict, List

import numpy as np
from PIL import Image, ImageCms
from insightface.app import FaceAnalysis


def to_srgb(image: Image) -> Image:
    icc = image.info.get("icc_profile", "")
    if icc:
        io_handle = io.BytesIO(icc)
        source_profile = ImageCms.ImageCmsProfile(io_handle)
        destination_profile = ImageCms.createProfile("sRGB")
        image = ImageCms.profileToProfile(image, source_profile, destination_profile)
    return image


DetectedFaces = List[Dict[str, Any]]


def detect_faces(image: Image) -> DetectedFaces:
    face_analysis = FaceAnalysis(allowed_modules=['detection', 'recognition'], rec_model='buffalo_l')
    face_analysis.prepare(ctx_id=-1, det_size=(1024, 1024))

    image = to_srgb(image)

    faces = face_analysis.get(np.array(image))

    result = [{
        "bbox": face["bbox"],
        "embedding": face["embedding"],
    } for face in faces]

    return result
