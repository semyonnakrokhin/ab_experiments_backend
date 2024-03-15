import logging.config

from dependency_injector import containers, providers

from apps.logging_config import LOGGING_CONFIG
from apps.src.database import DatabaseManager
from apps.src.db_service.config import DatabaseSettings
from apps.src.db_service.mappers import ExperimentsMapper
from apps.src.db_service.repositories import ExperimentRepository
from apps.src.db_service.services import DatabaseService
from apps.src.manager import ServiceManager
from apps.src.mappers import ExperimentsDomainDtoMapper
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


class MapperContainer(containers.DeclarativeContainer):
    experiments_mapper_provider = providers.Factory(ExperimentsMapper)

    experiments_domain_dto_mapper_provider = providers.Factory(
        ExperimentsDomainDtoMapper
    )


class RepositoryContainer(containers.DeclarativeContainer):
    mappers = providers.DependenciesContainer()

    experiment_repository_provider = providers.Factory(
        ExperimentRepository, mapper=mappers.experiments_mapper_provider
    )


class ServicesContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    database = providers.DependenciesContainer()

    mappers = providers.DependenciesContainer()

    database_service_provider = providers.Factory(
        DatabaseService,
        repository=repositories.experiment_repository_provider,
        async_session_factory=database.database_provider.provided.get_session_factory,
    )

    service_manager_provider = providers.Factory(
        ServiceManager,
        database_service=database_service_provider,
        mapper=mappers.experiments_domain_dto_mapper_provider,
    )


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    core = providers.Container(CoreContainer, config=config.logging)

    database = providers.Container(DatabaseContainer, config=config.database)

    mappers = providers.Container(MapperContainer)

    repositories = providers.Container(RepositoryContainer, mappers=mappers)

    services = providers.Container(
        ServicesContainer, repositories=repositories, database=database, mappers=mappers
    )


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
