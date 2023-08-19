from fastapi_listing.abstracts import DaoAbstract
from sqlalchemy.orm import Session

from fastapi_listing.ctyping import SqlAlchemyModel


# noinspection PyAbstractClass
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

    A dao should only have a primary table as we are speaking in terms of orm
    we will call it a model.
    so a dao should only be associated with single model or model class.
    for ex:
    model = ABCModelClass

    A naive layer for handling data related ops.
    """

    def __init__(self, read_db=None, write_db=None):
        """
        if you have a master slave architecture:
        read_db - read database session
        write_db - write database session
        if you have a single database:
        you can still reference read_db = write_db = same database session
        which will acts as a preparation to avoid changing pointing for each query,
        since we already have the basic setup injecting the right session(read_db = read database session,
        write_db = write database session) will save hours of debugging and fixing when needed.
        """
        self._read_db: Session = read_db
        self._write_db: Session = write_db

    def create(self, values) -> SqlAlchemyModel:
        """
        Subclasses can use this method to implement a generic method
        used for entering values into the database
        """
        raise NotImplementedError

    def update(self, identifier, values) -> bool:
        """
        Subclasses can use this method to implement a generic method
        used for updating values into the database against provided identifier
        which will be used to identify a set of unique records.
        The identifier can be used to uniquely identify a unique record or a bunch of records.
        """
        raise NotImplementedError

    def read(self, identifier, fields) -> SqlAlchemyModel:
        """
        Subclasses can use this method to implement a generic method
        used for reading values from the database against provided identifier.
        Use "fields" to fetch only specific fields or "__all__"
        """
        raise NotImplementedError

    def delete(self, identifier) -> bool:
        """
        Subclasses can use this method to implement a generic method
        used for deleting values from the database against provided identifier
        """
        raise NotImplementedError

    def get_default_read(self, fields_to_read: list):
        """
        Returns default model query with provided fields
        Subclasses can use this to write custom listing queries when
        there is no need for multiple queries.

        fields_to_read can be left or used.
        """
        return self._read_db.query(*fields_to_read)
