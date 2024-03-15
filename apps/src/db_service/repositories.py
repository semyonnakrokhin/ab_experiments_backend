import asyncio
import logging
from typing import Any, Dict, Generic, List, Optional, Type

from sqlalchemy import Float, Integer, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.src.app_types import D, E
from apps.src.db_service.abstract_mappers import AbstractDomainEntityMapper
from apps.src.db_service.abstract_repositories import AbstractDatabaseRepository
from apps.src.db_service.entities import ExperimentOrmModel
from apps.src.db_service.exceptions import (
    DatabaseError,
    InvalidParamsError,
    SessionNotSetError,
)
from apps.src.schemas import ExperimentsDomain

logger = logging.getLogger("fastapi_app.db_service.repositories")


class OrmAlchemyRepository(AbstractDatabaseRepository, Generic[E, D]):
    model: Optional[Type[E]] = None

    def __init__(self, mapper: AbstractDomainEntityMapper):
        self._session: Optional[AsyncSession] = None
        self._mapper = mapper

    def set_session(self, session: AsyncSession):
        if type(session) is not AsyncSession:
            error_message = (
                f"Session cannot be {type(session)}. Provide a valid AsyncSession."
            )
            logger.error(error_message)
            raise SessionNotSetError(error_message)

        self._session = session

    def clear_session(self):
        self._session = None

    def _validate_session_is_set(self):
        if self._session is None:
            error_message = (
                "Session not set. Call set_session() before using the repository."
            )
            logger.error(error_message)
            raise SessionNotSetError(error_message)

    async def insert_one(self, data: D) -> D:
        self._validate_session_is_set()

        entity = self._mapper.to_entity(domain_obj=data)

        stmt = insert(self.model).values(**entity.to_dict()).returning(self.model)
        try:
            result = await self._session.execute(stmt)
            entity_db = result.scalars().one()
        except Exception as e:
            error_message = (
                f"An error occurred while insert one file-metadata "
                f"to session and executing statement: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

        domain = self._mapper.to_domain(entity_obj=entity_db)

        return domain

    async def select_some_by_params(self, params: Dict[str, Any]) -> List[D]:
        self._validate_session_is_set()

        if type(params) != dict:
            error_message = "Type of params should be dict"
            logger.error(error_message)
            raise TypeError(error_message)

        model_fields = set(self.model.__table__.columns.keys())
        params_keys = set(params.keys())

        if not params_keys.issubset(model_fields):
            invalid_keys = params_keys - model_fields
            error_message = f"Some parameters do not match model fields: {invalid_keys}"
            logger.error(error_message)
            raise InvalidParamsError(error_message)

        query = select(self.model).filter_by(**params)
        try:
            result = await self._session.execute(query)
            entity_list = result.scalars().all()
        except Exception as e:
            error_message = (
                f"An error occurred while selecting one file-metadata "
                f"by its id and executing query: {str(e)}"
            )
            logger.error(error_message)
            raise DatabaseError(error_message)

        return [self._mapper.to_domain(entity_obj=entity) for entity in entity_list]


class ExperimentRepository(OrmAlchemyRepository[ExperimentOrmModel, ExperimentsDomain]):
    model = ExperimentOrmModel

    async def select_aggregated(self):
        self._validate_session_is_set()

        expr_columns = [
            col
            for col in self.model.__table__.columns
            if col.description not in ("id", "device_token")
        ]

        res_lst = []

        for expr_column in expr_columns:
            experiment_dict = {"experiment_name": expr_column.description, "data": []}
            subq = (
                select(
                    expr_column.label("option"),
                    func.count(expr_column).label("distribution"),
                )
                .group_by(expr_column)
                .order_by(expr_column.desc())
            ).subquery("helper1")

            subq_2 = select(
                subq.c.option,
                subq.c.distribution,
                func.sum(subq.c.distribution).over().cast(Integer).label("total"),
            ).subquery("helper2")

            cte = select(
                subq_2.c.option,
                subq_2.c.distribution,
                subq_2.c.total,
                func.round((subq_2.c.distribution / subq_2.c.total) * 100, 1)
                .cast(Float)
                .label("in_percentage"),
            )
            try:
                result = await self._session.execute(cte)
                experiment_dict["data"] += result.all()
            except Exception as e:
                error_message = (
                    f"An error occurred while insert one file-metadata "
                    f"to session and executing statement: {str(e)}"
                )
                logger.error(error_message)
                raise DatabaseError(error_message)

            res_lst.append(experiment_dict)

        return res_lst


if __name__ == "__main__":
    repo = ExperimentRepository()
    asyncio.run(repo.select_aggregated())
