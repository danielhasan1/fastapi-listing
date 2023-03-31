from abc import ABC, abstractmethod

from fastapi import Request

from fastapi_listing.abstracts import DaoAbstract


class QueryStrategy(ABC):

    @abstractmethod
    def get_query(self, *, field_list: list = None, request: Request = None, dao: DaoAbstract = None,
                  custom_fields: bool = None):
        pass
