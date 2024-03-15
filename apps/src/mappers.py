import logging
from abc import ABC, abstractmethod
from typing import Generic, Tuple

from apps.src.app_types import DTO, D
from apps.src.exceptions import DomainDtoMappingError
from apps.src.schemas import ColorExperimentDto, ExperimentsDomain, PriceExperimentDto

logger = logging.getLogger("app.mappers")


class AbstractDomainDtoMapper(ABC, Generic[D, DTO]):
    """AbstractDTOMapper is an abstract class providing a base interface for
    mappers that transform data from Data Transfer Objects (DTO) to the domain
    model."""

    @abstractmethod
    def to_dto(self, domain_obj: D) -> DTO:
        """Abstract method for mapping data from a source DTO object to a
        target domain model object.

        Args:
            domain_obj (D): The source Data Transfer Object (DTO) to be mapped.

        Returns:
            T: The target domain model object.
        """
        pass


class ExperimentsDomainDtoMapper(
    AbstractDomainDtoMapper[
        ExperimentsDomain, Tuple[ColorExperimentDto, PriceExperimentDto]
    ]
):
    def to_dto(
        self, domain_obj: ExperimentsDomain
    ) -> Tuple[ColorExperimentDto, PriceExperimentDto]:
        try:
            color_option = domain_obj.button_color
            price_option = domain_obj.price

            return (
                ColorExperimentDto(option=color_option),
                PriceExperimentDto(option=price_option),
            )
        except Exception as e:
            error_message = (
                f"An error occurred during mapping domain model to dto: {str(e)}"
            )
            logger.error(error_message)
            raise DomainDtoMappingError(error_message)
