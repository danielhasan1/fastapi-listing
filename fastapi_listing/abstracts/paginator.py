from abc import ABC, abstractmethod


class TableDataPaginatingStrategy(ABC):

    @property
    @abstractmethod
    def default_pagination_params(self):
        pass

    @abstractmethod
    def paginate(self, query, request):
        pass
