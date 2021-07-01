from fastapi import FastAPI

from .views import api_v1
from settings import config

tags_metadata = [
    {
        "name": "首页API",
        "description": "",
    },
]


def create_app():
    app = FastAPI(
        title="FastAPI",
        description="更多信息查看 ",
        version="0.1.1",
        docs_url=config.DOCS_URL,
        openapi_url=config.OPENAPI_URL,
        openapi_tags=tags_metadata
    )

    app.include_router(
        api_v1,
        prefix="/api/v1",
        # tags=["items"],
        # dependencies=[Depends(get_token_header)],
        # responses={404: {"description": "Not found"}},
    )

    return app
