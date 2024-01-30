__all__ = [
    "SqlAlchemyQuery",
    "SqlAlchemySession",
    "FastapiRequest",
    "AnySqlAlchemyColumn",
    "SqlAlchemyModel",
    "BasePage",
    "Page",
    "PageWithoutCount",
]

from typing import TypeVar, List, Dict, Union, Sequence, Generic
from typing_extensions import TypedDict
from fastapi import Request
from abc import ABC

# will support future imports as well like pymongo and other orm tools

try:
    from sqlalchemy.orm.decl_api import DeclarativeMeta
    from sqlalchemy.orm import Query
    from sqlalchemy.orm import Session
    from sqlalchemy.sql.sqltypes import TypeEngine
    from sqlalchemy.sql.schema import Column
    from sqlalchemy.engine.row import Row
except ImportError:
    DeclarativeMeta = None
    Query = None
    Session = None
    Column = None
    Row = False

T = TypeVar("T")


class BasePage(TypedDict):
    data: Sequence[T]


SqlAlchemyQuery = TypeVar("SqlAlchemyQuery", bound=Query)
SqlAlchemySession = TypeVar("SqlAlchemySession", bound=Session)
FastapiRequest = TypeVar("FastapiRequest", bound=Request)
AnySqlAlchemyColumn = TypeVar("AnySqlAlchemyColumn", bound=Column)
SqlAlchemyModel = TypeVar("SqlAlchemyModel", bound=DeclarativeMeta)

# sqlalchemy query objects returns mapper Row or Model object, or if extended user could roughly return a dict


class Page(BasePage):
    hasNext: bool
    totalCount: int
    currentPageSize: int
    currentPageNumber: int


class PageWithoutCount(BasePage):
    hasNext: bool
    currentPageSize: int
    currentPageNumber: int
