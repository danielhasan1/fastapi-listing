from typing import Optional

from abc import ABC, abstractmethod

from fastapi_listing.abstracts import DaoAbstract
from fastapi_listing.ctyping import FastapiRequest, SqlAlchemyQuery


class AbsQueryStrategy(ABC):

    @abstractmethod
    def get_query(self, *, request: Optional[FastapiRequest] = None, dao: DaoAbstract,
                  extra_context: dict) -> SqlAlchemyQuery:
        pass
