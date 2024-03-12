import logging

from apps.src.db_service.abstract_mappers import AbstractDomainEntityMapper
from apps.src.db_service.entities import ExperimentOrmModel
from apps.src.db_service.exceptions import MappingError
from apps.src.schemas import ExperimentsDto

logger = logging.getLogger("app.db_service.mappers")


class ExperimentsMapper(AbstractDomainEntityMapper[ExperimentsDto, ExperimentOrmModel]):
    def to_entity(self, domain_obj: ExperimentsDto) -> ExperimentOrmModel:
        try:
            return ExperimentOrmModel(**domain_obj.model_dump())
        except Exception as e:
            error_message = (
                f"An error occurred during mapping domain model to db entity: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)

    def to_domain(self, entity_obj: ExperimentOrmModel) -> ExperimentsDto:
        try:
            return ExperimentsDto.model_validate(obj=entity_obj, from_attributes=True)
        except Exception as e:
            error_message = (
                f"An error occurred during mapping entity model to domain: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)
