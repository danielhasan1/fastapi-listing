from fastapi_listing.abstracts import DaoAbstract
from sqlalchemy.orm import Session
from typing import Union, Dict, List

from fastapi_listing.typing import SqlAlchemyModel


class GenericDao(DaoAbstract):  # type:ignore # noqa
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

    # model: SqlAlchemyModel = None to be defined at model dao level

    def __init__(self, read_db=None, write_db=None):
        # considering that we are dealing with separate read and write dbs.
        # we must have two sessions one for read replica and one for master or write replica
        # we should define our reusable attributes here that we will use in each dao method definition
        # even if we are using single db still having two references for the same session won't hurt
        # for future expansion once we decide to move on to read/write replica architecure
        # we already have groundwork done and only need to push different connections
        # from request lifecycle layer.
        self._read_db: Session = read_db  # kwargs.get("read_db")
        self._write_db: Session = write_db  # kwargs.get("write_db")
        # if self.model is None:
        #     raise ValueError("model class is not set!")

    # def __setattr__(cls, name, value):
    #     if name == "model":
    #         raise AttributeError("Cannot modify .model")
    #     else:
    #         return type.__setattr__(cls, name, value)
    #
    # def __delattr__(cls, name):
    #     if name == "model":
    #         raise AttributeError("Cannot delete .model")
    #     else:
    #         return type.__delattr__(cls, name)

    def create(self, values: Dict[str, Union[str, int]]) -> SqlAlchemyModel:
        """
        A light method that enters values in primary model table.
        single value at a time receives a dict implementation could map the dict with model values and
        insert that mapping or single row into the table.
        :param values: dict of values where keys are columns of table and value should be row values
        :return: created object i.e., instrumented row object.
        """
        raise NotImplementedError

    def update(self, identifier: Dict[str, Union[str, int, list]], values: dict) -> bool:
        """
        Similar to create method this receives an identifier
        :param identifier:
        :param values:
        :return:
        """
        raise NotImplementedError

    def read(self, identifier: Dict[str, Union[str, int, list]],
             fields: Union[list, str] = "__all__") -> SqlAlchemyModel:
        raise NotImplementedError

    def delete(self, ids: List[int]) -> bool:
        raise NotImplementedError

    def get_naive_read(self, fields_to_read: list):
        return self._read_db.query(*fields_to_read)
