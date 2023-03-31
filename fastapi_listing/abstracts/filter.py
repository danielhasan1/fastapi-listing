from abc import ABC, abstractmethod


class FilterAbstract(ABC):

    @abstractmethod
    def filter(self, *, field: str = None, value: str = None, query=None):
        pass
