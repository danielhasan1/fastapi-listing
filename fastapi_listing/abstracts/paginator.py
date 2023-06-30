from abc import ABC, abstractmethod
from fastapi_listing.ctyping import SqlAlchemyQuery, FastapiRequest


class AbsPaginatingStrategy(ABC):

    @abstractmethod
    def paginate(self, query: SqlAlchemyQuery, pagination_params: dict, extra_context: dict):
        pass
