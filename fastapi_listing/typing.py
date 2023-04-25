from typing import TypeVar, List, Dict
from typing_extensions import TypedDict
from fastapi import Request

# will support future imports as well like pymongo and other orm tools

try:
    from sqlalchemy.orm.decl_api import DeclarativeMeta
    from sqlalchemy.orm import Query
    from sqlalchemy.orm import Session
    from sqlalchemy.sql.sqltypes import TypeEngine
except ImportError:
    DeclarativeMeta = None
    Query = None
    Session = None
    TypeEngine = None


class ListingResponseType(TypedDict):
    data: List[Dict[str, int | str | list | dict]]
    currentPageNumber: int
    currentPageSize: int
    totalCount: int
    hasNext: bool


SqlAlchemyQuery = TypeVar("SqlAlchemyQuery", bound=Query)
SqlAlchemySession = TypeVar("SqlAlchemySession", bound=Session)
FastapiRequest = TypeVar("FastapiRequest", bound=Request)
AnySqlAlchemyColumn = TypeVar("AnySqlAlchemyColumn", bound=TypeEngine)
SqlAlchemyModel = TypeVar("SqlAlchemyModel", bound=DeclarativeMeta)

