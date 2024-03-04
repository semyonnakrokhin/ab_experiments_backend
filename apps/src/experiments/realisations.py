from itertools import cycle
from random import shuffle

from apps.src.experiments.abstractions import AbstractExperiment


class ColorExperiment(AbstractExperiment):
    def __init__(self):
        self.colors = cycle(["#FF0000", "#00FF00", "#0000FF"])

    def get_option(self):
        return next(self.colors)


class PriceExperiment(AbstractExperiment):
    def __init__(self):
        prices = ([10] * 15) + ([20] * 2) + ([50] * 1) + ([5] * 2)
        shuffle(prices)
        self.prices = cycle(prices)

    def get_option(self):
        return next(self.prices)
