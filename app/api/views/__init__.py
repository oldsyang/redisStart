from fastapi import APIRouter

from . import index

api_v1 = APIRouter()

api_v1.include_router(index.router, tags=["index"])
