import logging
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from apps.src.db_service.exceptions import (
    DatabaseError,
    DatabaseServiceError,
    MappingError,
    SessionNotSetError,
)
from apps.src.db_service.repositories import ExperimentRepository
from apps.src.schemas import ExperimentsDto

logger = logging.getLogger("fastapi_app.db_service.services")


class DatabaseService:
    def __init__(
        self,
        repository: ExperimentRepository,
        async_session_factory: async_sessionmaker,
    ):
        self._repository = repository
        self._async_session_factory = async_session_factory

    async def add_experiments(self, experiments: ExperimentsDto) -> ExperimentsDto:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                experiments_output = await self._repository.insert_one(data=experiments)
                await session.commit()

            return experiments_output

        except (SessionNotSetError, MappingError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"adding the experiments to database "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()

    async def get_experiments_by_device_token(
        self, device_token: str
    ) -> Optional[ExperimentsDto]:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                experiments_output_lst = await self._repository.select_some_by_params(
                    params={"device_token": device_token}
                )

            return experiments_output_lst[0] if experiments_output_lst else None

        except (
            SessionNotSetError,
            MappingError,
            DatabaseError,
            AttributeError,
            TypeError,
        ) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"getting the experiments with "
                f"device_token={device_token} from database "
                f"on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()

    async def get_statistics_on_all_experiments(self) -> List[Dict]:
        try:
            async with self._async_session_factory() as session:
                self._repository.set_session(session)
                statistics_lst = await self._repository.select_aggregated()

            return statistics_lst

        except (SessionNotSetError, DatabaseError, AttributeError) as e:
            raise e
        except Exception as e:
            error_message = (
                f"An error occurred while "
                f"collecting statistics on all the experiments with "
                f"from database on service or repository layer: {e}"
            )
            logger.error(error_message)
            raise DatabaseServiceError(error_message)
        finally:
            self._repository.clear_session()
