import uvicorn
from fastapi import FastAPI

from apps.src.api.router import router as router_api
from apps.src.pages.router import router as router_pages


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router_api)
    app.include_router(router_pages)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
