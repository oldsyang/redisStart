#!/usr/bin/env python
from api import create_app
from settings import config

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app='main:app', host="0.0.0.0", port=config.WEB_PORT, reload=True, debug=True)
