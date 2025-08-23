from fastapi import APIRouter

from app.api.routes import ping
from app.api.routes import search
from app.api.routes import vectorize

api_router = APIRouter()
api_router.include_router(vectorize.router)
api_router.include_router(search.router)

common_api_router = APIRouter()
common_api_router.include_router(ping.router)
