from celery import shared_task

from apps.src.experiments.realisations import ColorExperiment, PriceExperiment

# from apps.src.task_queue.celery_setup import celery_app


_color_experiment = ColorExperiment()
_price_experiment = PriceExperiment()


#
# @celery_app.task
@shared_task
def color_experiment_task():
    return _color_experiment.get_option()


# @celery_app.task
@shared_task
def price_experiment_task():
    return _price_experiment.get_option()
