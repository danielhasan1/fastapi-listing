from fastapi_listing.abstracts import DaoAbstract
from sqlalchemy.orm import Session

from fastapi_listing.typing import SqlAlchemyModel


class GenericDao(DaoAbstract):
    """
    Dao stands for data access object.
    This layers encapsulates all logic that a user may write
    in order to interact with databases.
    Dao has only one responsibility that is to communicate with
    database, all logic regarding data manipulation should live at
    service layer. This also acts as a gateway to database
    a wrapper on top of existing orm where generic logic could be defined.

    This is a demo class showing how one can benefit from it.
    Please note that this is just a basic implementation
    i.e., a basic recipe, if one want they can spice it up as they like.

    A dao should only have a primary table as we are speaking in terms of orm
    we will call it a model.
    so a dao should only be associated with single model or model class.
    i.e., one primary model per dao instance. please note that this is different from
    joining multiple models or tables. we are strictly  speaking in terms of
    objects context here that one dao object should only have one primary model
    but one dao object can talk to multiple models with having first primary model.

    Note - no data validation should happen at this layer. That should be prior to pushing
    at this layer.
    """

    model_kls: SqlAlchemyModel = None

    def __init__(self, **kwargs):
        # considering that we are dealing with separate read and write dbs.
        # we must have two sessions one for read replica and one for master or write replica
        # we should define our reusable attributes here that we will use in each dao method definition
        self._read_db: Session = kwargs.get("read_db")
        self._write_db: Session = kwargs.get("write_db")
        if self.model_kls is None:
            raise ValueError("model class is not set!")
        self.model = self.model_kls

    def create(self, values: dict[str, str | int]) -> SqlAlchemyModel:
        """
        A light method that enters values in primary model table.
        single value at a time receives a dict implementation could map the dict with model values and
        insert that mapping or single row into the table.
        :param values: dict of values where keys are columns of table and value should be row values
        :return: created object i.e., instrumented row object.
        """
        pass

    def update(self, identifier: dict[str, str | int | list], values: dict) -> bool:
        """
        Similar to create method this receives an identifier
        :param identifier:
        :param values:
        :return:
        """
        pass

    def read(self, identifier: dict[str, str | int | list], fields: list | str = "__all__") -> SqlAlchemyModel:
        pass

    def delete(self, ids: list[int]) -> bool:
        pass

    def get_naive_read(self, fields_to_read: list):
        return self._read_db.query(*fields_to_read)
