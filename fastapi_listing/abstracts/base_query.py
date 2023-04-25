from abc import ABC, abstractmethod

from fastapi import Request

from fastapi_listing.abstracts import DaoAbstract


class QueryStrategy(ABC):

    @abstractmethod
    def get_query(self, *, request: Request = None, dao: DaoAbstract = None, extra_context: dict = None):
        pass
