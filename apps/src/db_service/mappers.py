import logging

from apps.src.db_service.abstract_mappers import AbstractDomainEntityMapper
from apps.src.db_service.entities import ExperimentOrmModel
from apps.src.db_service.exceptions import MappingError
from apps.src.schemas import ColorOptions, ExperimentsDomain, PriceOptions

logger = logging.getLogger("app.db_service.mappers")


class ExperimentsMapper(
    AbstractDomainEntityMapper[ExperimentsDomain, ExperimentOrmModel]
):
    def to_entity(self, domain_obj: ExperimentsDomain) -> ExperimentOrmModel:
        try:
            return ExperimentOrmModel(
                device_token=domain_obj.device_token,
                button_color=domain_obj.button_color.value,
                price=domain_obj.price.value,
            )
        except Exception as e:
            error_message = (
                f"An error occurred during mapping domain model to db entity: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)

    def to_domain(self, entity_obj: ExperimentOrmModel) -> ExperimentsDomain:
        try:
            return ExperimentsDomain(
                device_token=entity_obj.device_token,
                button_color=ColorOptions(entity_obj.button_color),
                price=PriceOptions(entity_obj.price),
            )
        except Exception as e:
            error_message = (
                f"An error occurred during mapping entity model to domain: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)
