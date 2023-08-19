from abc import ABC, abstractmethod
from fastapi_listing.ctyping import SqlAlchemyQuery, BasePage


class AbsPaginatingStrategy(ABC):

    @abstractmethod
    def paginate(self, query: SqlAlchemyQuery, pagination_params: dict, extra_context: dict) -> BasePage:
        pass
