from abc import ABC, abstractmethod


class TableDataSortingStrategy(ABC):

    @abstractmethod
    def sort(self, *, query=None, request=None, model=None, field_mapper=None):
        pass
