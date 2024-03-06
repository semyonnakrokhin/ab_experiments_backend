from apps.src.experiments.realisations import ColorExperiment, PriceExperiment
from apps.src.main import celery_app


@celery_app.task
def color_experiment_task():
    experiment = ColorExperiment()
    return experiment.get_option()


@celery_app.task
def price_experiment_task():
    experiment = PriceExperiment()
    return experiment.get_option()
