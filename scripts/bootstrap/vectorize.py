from pathlib import Path
from typing import Any, Dict

import requests


def vectorize_photo(configuration: Dict[str, Any], file_path: Path):
    vectorize_service_url = configuration["vectorize"]["url"]

    with open(file_path.resolve(), "rb") as file:
        files_to_vectorize = {"file": (file_path.name, file, "image/jpeg")}
        response = requests.post(vectorize_service_url, files=files_to_vectorize)

        if response.status_code == 200:
            print(f"[{file_path.name}] Успешно")
        else:
            print(f"[{file_path.name}] Ошибка: {response.status_code}, {response.text}")
