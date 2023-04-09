from fastapi_listing.factory import generic_factory
from fastapi_listing.abstracts import TableDataSortingStrategy
from fastapi_listing.typing import SqlAlchemyQuery


class SorterMechanics:

    def apply(self, *, query: SqlAlchemyQuery = None, strategy: TableDataSortingStrategy = None,
              sorting_params: list[dict[str, str]] = None) -> SqlAlchemyQuery:
        latest = sorting_params[-1]
        query = strategy.sort(query=query, value=latest)
        return query


def register() -> None:
    generic_factory.register("sorter_mechanics", SorterMechanics)
