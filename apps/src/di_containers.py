import logging.config

from dependency_injector import containers, providers

from apps.logging_config import LOGGING_CONFIG
from apps.src.database import DatabaseManager
from apps.src.db_service.config import DatabaseSettings
from apps.src.manager import ServiceManager
from apps.src.utils import merge_dicts


class CoreContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging_provider = providers.Resource(
        logging.config.dictConfig,
        config=config,
    )


class DatabaseContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    database_provider = providers.Singleton(DatabaseManager, db_url=config.dsn)


class ServicesContainer(containers.DeclarativeContainer):
    service_manager_provider = providers.Factory(ServiceManager)


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    core = providers.Container(CoreContainer, config=config.logging)

    database = providers.Container(DatabaseContainer, config=config.database)

    services = providers.Container(ServicesContainer)


if __name__ == "__main__":
    db_settings = DatabaseSettings()
    log_settings_dict = LOGGING_CONFIG
    settings_dict = merge_dicts(
        {"database": db_settings.model_dump()}, {"logging": log_settings_dict}
    )

    container = AppContainer()
    container.config.from_dict(settings_dict)
    container.core.init_resources()

    db = container.database.database_provider()
    c = 1
