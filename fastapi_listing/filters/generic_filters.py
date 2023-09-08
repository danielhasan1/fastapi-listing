__all__ = [
    "CommonFilterImpl",
    "EqualityFilter",
    "InEqualityFilter",
    "InDataFilter",
    "BetweenUnixMilliSecDateFilter",
    "StringStartsWithFilter",
    "StringEndsWithFilter",
    "StringContainsFilter",
    "StringLikeFilter",
    "DataGreaterThanFilter",
    "DataGreaterThanEqualToFilter",
    "DataLessThanFilter",
    "DataLessThanEqualToFilter",
    "DataGropByElementFilter",
    "DataDistinctByElementFilter",
    "HasFieldValue",
    "MySqlNativeDateFormateRangeFilter",
]

from typing import Callable, Optional
from datetime import datetime

from fastapi import Request

from fastapi_listing.abstracts import FilterAbstract
from fastapi_listing.ctyping import SqlAlchemyQuery, AnySqlAlchemyColumn


class CommonFilterImpl(FilterAbstract):

    def __init__(self, dao=None, request: Optional[Request] = None, *, extra_context: dict,
                 field_extract_fn: Callable[[str], AnySqlAlchemyColumn]):
        # lambda x: getattr(Model, x)
        self.dao = dao
        self.request = request
        self.extra_context = extra_context
        self.custom_field_extractor = field_extract_fn

    def extract_field(self, field: str) -> AnySqlAlchemyColumn:
        field = field.split(".")[-1]
        if self.custom_field_extractor:
            return self.custom_field_extractor(field)
        return getattr(self.dao.model, field)

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        raise NotImplementedError("To be implemented in child class!")


class EqualityFilter(CommonFilterImpl):

    def filter(self, *, field=None, value=None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field == value.get("search"))
        return query


class InEqualityFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field != value.get("search"))
        return query


class InDataFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field.in_(value.get("list")))
        return query


class BetweenUnixMilliSecDateFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field.between(datetime.fromtimestamp(int(value.get('start')) / 1000),
                                                    datetime.fromtimestamp(int(value.get('end')) / 1000)))
        return query


class StringStartsWithFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field.startswith(value.get("search")))
        return query


class StringEndsWithFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field.endswith(value.get("search")))
        return query


class StringContainsFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field.contains(value.get("search")))
        return query


class StringLikeFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field.like(value.get("search")))
        return query


class DataGreaterThanFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field > value.get("search"))
        return query


class DataGreaterThanEqualToFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field >= value.get("search"))
        return query


class DataLessThanFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field < value.get("search"))
        return query


class DataLessThanEqualToFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field <= value.get("search"))
        return query


class DataGropByElementFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        query = query.group_by(inst_field)
        return query


class DataDistinctByElementFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        query = query.distinct(inst_field)
        return query


class HasFieldValue(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value.get("search"):
            query = query.filter(inst_field.is_not(None))
        else:
            query = query.filter(inst_field.is_(None))
        return query


class MySqlNativeDateFormateRangeFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None) -> SqlAlchemyQuery:
        inst_field = self.extract_field(field)
        if value:
            query = query.filter(inst_field.between(value.get("start"), value.get("end")))
        return query
