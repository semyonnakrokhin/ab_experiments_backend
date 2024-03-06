from celery import shared_task

from apps.src.experiments.realisations import ColorExperiment, PriceExperiment


@shared_task
def color_experiment_task():
    experiment = ColorExperiment()
    return experiment.get_option()


@shared_task
def price_experiment_task():
    experiment = PriceExperiment()
    return experiment.get_option()
