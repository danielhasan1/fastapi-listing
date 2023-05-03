from abc import ABC, abstractmethod

from fastapi_listing.abstracts import DaoAbstract
from fastapi_listing.typing import FastapiRequest, SqlAlchemyQuery


class QueryStrategy(ABC):

    @abstractmethod
    def get_query(self, *, request: FastapiRequest = None, dao: DaoAbstract = None,
                  extra_context: dict = None) -> SqlAlchemyQuery:
        pass
