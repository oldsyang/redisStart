from fastapi import APIRouter, Request

from utils import response_code

router = APIRouter()


@router.get("/heart/", summary="心跳")
async def heart(request: Request):
    """:arg"""

    return response_code.resp_200({})
