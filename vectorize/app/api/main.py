from fastapi import APIRouter

from app.api.routes import vectorize

api_router = APIRouter()
api_router.include_router(vectorize.router)
