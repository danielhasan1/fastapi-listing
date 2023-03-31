from typing import Tuple, TypeVar, List, Dict
from typing_extensions import TypedDict
from sqlalchemy.orm.decl_api import DeclarativeMeta


SqlAlchemyModel = TypeVar("SqlAlchemyModel", bound=DeclarativeMeta)


class ListingResponseType(TypedDict):
    data: List[Dict[str, int | str | list | dict]]
    currentPageNumber: int
    currentPageSize: int
    totalCount: int
    hasNext: bool
