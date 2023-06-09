from abc import ABC, abstractmethod
from fastapi_listing.typing import SqlAlchemyQuery, FastapiRequest


class AbsPaginatingStrategy(ABC):

    @property
    @abstractmethod
    def default_pagination_params(self):
        pass

    @abstractmethod
    def paginate(self, query: SqlAlchemyQuery, request: FastapiRequest, extra_context: dict):
        pass
