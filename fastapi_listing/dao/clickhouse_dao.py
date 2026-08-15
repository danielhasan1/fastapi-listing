"""Reference non-ORM backend: a DAO that talks raw ClickHouse SQL through
`clickhouse-driver`, proving the QueryContext abstraction generalizes beyond
SQLAlchemy.

Subclasses set `name` and `model` exactly like GenericDao subclasses do, except
`model` is a plain class whose attributes are column-name strings (no
declarative base, no ORM) - e.g.:

    class Employee:
        __table__ = "employees"
        id = "id"
        name = "name"

`getattr(Employee, "name")` then resolves to the string "name", which is all
CanonicalFilter.extract_field() / SortingOrderStrategy.validate_srt_field()
ever need - both already just do `getattr(model, field)`, unchanged.
"""

from fastapi_listing.abstracts import DaoAbstract
from fastapi_listing.context.clickhouse import ClickHouseQueryContext


class ClickHouseDao(DaoAbstract):

    def __init__(self, read_db=None, write_db=None):
        """
        read_db/write_db are expected to be `clickhouse_driver.Client`
        instances (or anything exposing the same `.execute()` signature -
        including a fake client in tests).
        """
        self._read_db = read_db
        self._write_db = write_db

    def create(self, values):
        raise NotImplementedError("ClickHouse's mutation model doesn't map to CRUD; implement per-DAO if needed.")

    def update(self, identifier, values):
        raise NotImplementedError("ClickHouse's mutation model doesn't map to CRUD; implement per-DAO if needed.")

    def read(self, identifier, fields):
        raise NotImplementedError("ClickHouse's mutation model doesn't map to CRUD; implement per-DAO if needed.")

    def delete(self, identifier):
        raise NotImplementedError("ClickHouse's mutation model doesn't map to CRUD; implement per-DAO if needed.")

    def get_default_read(self, fields_to_read: list):
        table = getattr(self.model, "__table__", None) or self.model.__name__.lower()
        return ClickHouseQueryContext(client=self._read_db, table=table, columns=fields_to_read)
