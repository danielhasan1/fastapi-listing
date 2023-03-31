from datetime import datetime

from fastapi_listing.abstracts import FilterAbstract


class CommonFilterImpl(FilterAbstract):

    def __init__(self, dao=None, request=None, **kwargs):
        self.dao = dao
        self.request = request

    def filter(self, *, field: str = None, value: dict = None, query=None):
        raise NotImplementedError("To be implemented in child class!")


class EqualityFilter(CommonFilterImpl):

    def filter(self, *, field=None, value=None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])

        query = query.filter(inst_field == value.get("search"))
        return query


class InEqualityFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        if value:
            query = query.filter(inst_field != value.get("search"))
        return query


class InDataFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field.in_(value.get("list")))
        return query


class BetweenDateFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field.between(datetime.fromtimestamp(int(value.get('start')) / 1000),
                                                datetime.fromtimestamp(int(value.get('end')) / 1000)))
        return query


class StringStartsWithFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field.startswith(value.get("search")))
        return query


class StringEndsWithFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field.endswith(value.get("search")))
        return query


class StringContainsFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field.contains(value.get("search")))
        return query


class StringLikeFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field.like(value.get("search")))
        return query


class DataGreaterThanFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field > value.get("search"))
        return query


class DataGreaterThanEqualToFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field >= value.get("search"))
        return query


class DataLessThanFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field < value.get("search"))
        return query


class DataLessThanEqualToFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.filter(inst_field <= value.get("search"))
        return query


class DataGropByElementFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.group_by(inst_field)
        return query


class DataDistinctByElementFilter(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        query = query.distinct(inst_field)
        return query


class HasFieldValue(CommonFilterImpl):

    def filter(self, *, field: str = None, value: dict = None, query=None):
        inst_field = getattr(self.dao.model, field.split(".")[1])
        if value.get("search"):
            query = query.filter(inst_field.is_not(None))
        else:
            query = query.filter(inst_field.is_(None))
        return query
