import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from apps.src.database import DatabaseManager
from apps.src.db_service.config import DatabaseSettings
from apps.src.db_service.entities import ExperimentOrmModel
from apps.src.experiments.realisations import ColorExperiment, PriceExperiment
from apps.src.main import fastapi_app
from apps.src.utils import generate_device_token


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def container():
    container = fastapi_app.container

    return container


@pytest.fixture(scope="session")
def database_test(container):
    return container.database.database_provider()


@pytest.fixture(scope="session", autouse=True)
async def setup_db(database_test):
    assert DatabaseSettings().mode == "TEST"

    await database_test.delete_and_create_database()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=False)
async def insert_data_to_database(database_test: DatabaseManager):
    color_experiment = ColorExperiment()
    price_experiment = PriceExperiment()

    await database_test.delete_and_create_database()

    async with database_test.get_session_factory() as session:
        for _ in range(20):
            device_token = generate_device_token()

            button_color = color_experiment.get_option()
            price = price_experiment.get_option()

            session.add(
                ExperimentOrmModel(
                    device_token=device_token, button_color=button_color, price=price
                )
            )

        await session.commit()


@pytest.fixture(scope="function", autouse=False)
async def empty_database(database_test):
    await database_test.delete_and_create_database()


@pytest.fixture(scope="session")
def celery_config():
    # return {
    #     "broker_url": "redis://127.0.0.1:6379/0",
    #     "result_backend": "redis://127.0.0.1:6379/1",
    #     "task_always_eager": True,
    # }
    return {
        "broker_url": "memory://",
        "result_backend": "rpc://",
        "task_always_eager": True,
    }


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {"perform_ping_check": False, "worker_pool": "solo"}


# @pytest.fixture(scope="session")
# def celery_includes():
#     return ["apps.src.task_queue.tasks"]
