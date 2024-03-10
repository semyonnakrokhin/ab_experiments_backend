import pytest


@pytest.fixture(scope="session", autouse=False)
def conduct_experiments(container):
    service_manager = container.services.service_manager_provider()
    f = service_manager.conduct_experiments
    return f
