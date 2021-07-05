import traceback

import databases
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette import status

from api.models import Base
from common.database import _db, db_engine
from common.redis import _redis
from extensions import logger
from settings import config
from utils.custom_exc import Error, PostParamsError, ResponseCode, TokenAuthError, UserTokenError
from .views import api_v1

tags_metadata = [
    {
        "name": "首页API",
        "description": "",
    },
]


def register_db(app: FastAPI) -> None:
    """
    把redis挂载到app对象上面
    :param app:
    :return:
    """

    @app.on_event('startup')
    async def startup_event():
        """
        获取链接
        :return:
        """
        import traceback
        try:
            db = databases.Database(config.DB_URL.replace('+pymysql', ''))
            await db.connect()
        except:
            traceback.print_exc()
            raise
        else:
            app.state.db = db

    @app.on_event('shutdown')
    async def shutdown_event():
        """
        关闭
        :return:
        """
        try:
            await app.state.db.disconnect()
            logger.info("shutdown db")
            if _redis:
                await _redis.close()
                logger.info("shutdown _redis")
            if _db:
                await _db.disconnect()
                logger.info("shutdown _db")

            logger.info("shutdown over")
        except Exception as e:
            traceback.print_exc()
            pass


def create_app():
    app = FastAPI(
        title="FastAPI",
        description="更多信息查看 ",
        version="0.1.1",
        docs_url=config.DOCS_URL,
        openapi_url=config.OPENAPI_URL,
        openapi_tags=tags_metadata
    )
    target_metadata = Base.metadata
    target_metadata.create_all(db_engine)

    app.include_router(
        api_v1,
        prefix="/api/v1",
        # tags=["items"],
        # dependencies=[Depends(get_token_header)],
        # responses={404: {"description": "Not found"}},
    )

    register_db(app)

    return app


def register_exception(app: FastAPI):
    """
    全局异常捕获
    :param app:
    :return:
    """

    # 捕获自定义异常
    @app.exception_handler(PostParamsError)
    async def query_params_exception_handler(request: Request, exc: PostParamsError):
        """
        捕获 自定义抛出的异常
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"参数查询异常\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "meta": {"error_code": ResponseCode.PARAMS_NOT_VALID,
                         "message": "{}-{}".format(exc.field, exc.err_desc)}, "data": {}
            }
        )

    @app.exception_handler(TokenAuthError)
    @app.exception_handler(UserTokenError)
    async def token_exception_handler(request: Request, exc: TokenAuthError):
        logger.error(f"参数查询异常\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "meta": {"error_code": ResponseCode.TOKEN_NOT_VALID,
                         "message": exc.err_desc}, "data": {}
            },
        )

    # 捕获参数 验证错误
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        捕获请求参数 验证错误
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"参数错误\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        errors = exc.errors()[0]
        logger.warning(23)
        logger.warning(errors)
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                {
                    "meta": {"error_code": ResponseCode.PARAMS_NOT_VALID,
                             "message": "{} {}".format(errors["loc"][1], errors["msg"])}, "data": {}
                }
            ),
        )  # 捕获参数 验证错误

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """
        捕获请求参数 验证错误
        :param request:
        :param exc:
        :return:
        """
        logger.error(f"参数错误\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        errors = exc.errors()[0]
        logger.warning(errors)
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                {
                    "meta": {"error_code": ResponseCode.PARAMS_NOT_VALID,
                             "message": "{} {}".format(errors["loc"][0], errors["msg"])}, "data": {}
                }
            ),
        )

    @app.exception_handler(Error)
    async def all_exception_handler(request: Request, exc: Error):
        logger.error(f"自定义错误\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=
            {
                "meta": {"error_code": exc.code,
                         "message": exc.message}, "data": {}
            }
        )

    # 捕获全部异常
    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        logger.error(f"全局异常\nURL:{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "meta": {"error_code": 500,
                         "message": '服务器错误'}, "data": {}
            }
        )
