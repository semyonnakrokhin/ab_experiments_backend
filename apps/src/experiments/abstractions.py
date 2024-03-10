from abc import ABC, abstractmethod


class AbstractExperiment(ABC):
    @abstractmethod
    def get_option(self):
        pass
