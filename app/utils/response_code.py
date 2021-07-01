from typing import Union

from fastapi import status
from fastapi.responses import JSONResponse, ORJSONResponse, Response

from utils.custom_exc import ResponseCode


def resp_200_str(data: str = None) -> object:
    return Response(status_code=status.HTTP_200_OK, content=data)


def resp_200(data: object = None, status: object = ResponseCode.SUCCESS_CODE, *,
             message: object = "Success") -> object:
    return data


def resp_400(data: str = None) -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=data
    )


def resp_403(data: str = None) -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            'code': 403,
            'message': "Forbidden",
            'data': data,
        }
    )


def resp_404(data: str = None) -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'code': 404,
            'message': "Page Not Found",
            'data': data,
        }
    )


def resp_500(data: str = None) -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'code': "500",
            'message': "Server internal error",
            'data': data,
        }
    )


# 自定义
def resp_5000(data: Union[list, dict, str]) -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': 5000,
            'message': "Token failure",
            'data': data,
        }
    )
