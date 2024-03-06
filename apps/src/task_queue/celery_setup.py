from celery import Celery


def create_celery(config_module: str) -> Celery:
    app = Celery()
    app.config_from_object(obj=config_module)

    return app
