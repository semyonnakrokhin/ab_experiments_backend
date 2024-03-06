import uvicorn
from fastapi import FastAPI

from apps.logging_config import LOGGING_CONFIG
from apps.src.api.router import router as router_api
from apps.src.db_service.config import DatabaseSettings
from apps.src.di_containers import AppContainer
from apps.src.pages.router import router as router_pages
from apps.src.task_queue.celery_setup import create_celery
from apps.src.utils import merge_dicts


def create_fastapi_app() -> FastAPI:
    db_settings = DatabaseSettings()
    log_settings_dict = LOGGING_CONFIG
    settings_dict = merge_dicts(
        {"database": db_settings.model_dump()}, {"logging": log_settings_dict}
    )

    container = AppContainer()
    container.config.from_dict(settings_dict)
    container.core.init_resources()
    container.wire(modules=["apps.src.api.router", "apps.src.pages.router"])

    app = FastAPI()
    app.container = container
    app.include_router(router_api)
    app.include_router(router_pages)

    return app


fastapi_app = create_fastapi_app()

celery_app = create_celery(config_module="apps.src.task_queue.celeryconfig")


if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
