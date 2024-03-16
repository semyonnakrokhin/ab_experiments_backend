import logging
from typing import Any, Dict, List

from celery import group

from apps.src.db_service.services import DatabaseService
from apps.src.exceptions import ExperimentError
from apps.src.mappers import AbstractDomainDtoMapper
from apps.src.schemas import ExperimentsDomain, ExperimentsDto
from apps.src.task_queue.tasks import color_experiment_task, price_experiment_task

logger = logging.getLogger("fastapi_app.service_manager")


class ServiceManager:
    def __init__(
        self, database_service: DatabaseService, mapper: AbstractDomainDtoMapper
    ):
        self._database_service = database_service
        self._mapper = mapper

    @staticmethod
    def conduct_experiments() -> Dict[str, Any]:
        tasks_parallel = group(
            color_experiment_task.s().set(queue="button"),
            price_experiment_task.s().set(queue="price"),
        )

        async_result = tasks_parallel.apply_async(retry=False, timeout=3)

        if async_result.failed():
            error_message = (
                "One or more experiments failed to execute. "
                "Check the async result for details."
            )
            logger.error(error_message)
            raise ExperimentError(error_message)

        try:
            options_lst = async_result.get(timeout=4, propagate=True)
        except Exception as e:
            error_message = (
                f"Failed to retrieve experiment results: {str(e)} "
                f"due to connection to result backend fail"
            )
            logger.error(error_message)
            raise ExperimentError(error_message)

        payload = {"button_color": options_lst[0], "price": options_lst[1]}

        return payload

    # @staticmethod
    # def conduct_experiments():
    #     c_task = color_experiment_task.s().set(queue="button")
    #     p_task = price_experiment_task.s().set(queue="price")
    #
    #     c_res = c_task.apply_async()
    #     p_res = p_task.apply_async()
    #
    #     try:
    #         options_lst = [
    #             c_res.get(propagate=True),
    #             p_res.get(propagate=True)
    #         ]
    #     except Exception as e:
    #         error_message = (
    #             f"Failed to retrieve experiment results: {str(e)} "
    #             f"due to connection to result backend fail"
    #         )
    #         logger.error(error_message)
    #         raise ExperimentError(error_message)
    #
    #     payload = {"button_color": options_lst[0], "price": options_lst[1]}
    #
    #     return payload

    async def get_or_conduct_experiments(
        self, device_token: str
    ) -> List[ExperimentsDto]:
        experiments = await self._database_service.get_experiments_by_device_token(
            device_token=device_token
        )

        if not experiments:
            conducted_experiments = self.conduct_experiments()
            experiments = await self._database_service.add_experiments(
                experiments=ExperimentsDomain(
                    device_token=device_token, **conducted_experiments
                )
            )

        return list(self._mapper.to_dto(domain_obj=experiments))

    async def get_statistics_for_web_page(self) -> List[Dict]:
        statistics_lst = (
            await self._database_service.get_statistics_on_all_experiments()
        )
        return statistics_lst
