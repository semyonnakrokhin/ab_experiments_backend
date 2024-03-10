import logging
from typing import List

from celery import group

from apps.src.exceptions import ExperimentError
from apps.src.schemas import ColorExperimentDto, ExperimentModel, PriceExperimentDto
from apps.src.task_queue.tasks import color_experiment_task, price_experiment_task

logger = logging.getLogger("app.service_manager")


class AbstractDatabaseService:
    pass


class ServiceManager:
    def __init__(self, database_service: AbstractDatabaseService = None):
        self._database_service = database_service

    @staticmethod
    def conduct_experiments() -> List[ExperimentModel]:
        tasks_parallel = group(
            color_experiment_task.s().set(queue="button"),
            price_experiment_task.s().set(queue="price"),
        )

        async_result = tasks_parallel.apply_async()

        if async_result.failed():
            error_message = (
                "One or more experiments failed to execute. "
                "Check the async result for details."
            )
            logger.error(error_message)
            raise ExperimentError(error_message)

        options_lst = async_result.get()
        experiments_lst = [
            ColorExperimentDto(option=options_lst[0]),
            PriceExperimentDto(option=options_lst[1]),
        ]

        return experiments_lst

    async def get_or_conduct_experiments(
        self, device_token: str
    ) -> List[ExperimentModel]:
        # experiments_lst = self._database_service
        # .get_experiments_by_token(device_token=device_token)
        experiments_lst = None

        if not experiments_lst:
            experiments_lst = self.conduct_experiments()

        return experiments_lst
