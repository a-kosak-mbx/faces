import json

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from app.api.main import api_router, common_api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(common_api_router)

if __name__ == "__main__":
    schema = get_openapi(
        title="Vectorize API",
        version="0.1.0",
        description="Векторизация изображений и поиск",
        routes=app.routes,
    )

    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
