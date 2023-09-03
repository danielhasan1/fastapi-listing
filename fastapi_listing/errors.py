from fastapi import HTTPException


class FastapiListingError(BaseException):
    pass


class ListingFilterError(FastapiListingError):
    pass


class ListingSorterError(FastapiListingError):
    pass


class ListingPaginatorError(FastapiListingError):
    pass


class NotRegisteredApiException(HTTPException):
    pass


class FastapiListingRequestSemanticApiException(HTTPException):
    pass


class MissingSessionError(Exception):
    """Exception raised for when the user tries to access a database session before it is created."""

    def __init__(self):
        msg = """
        No session found! Either you are not currently in a request context,
        or you need to manually create a session context and pass the callable to middleware args
        e.g.
        callable -> get_db
        app.add_middleware(DaoSessionBinderMiddleware, master=get_db, replica=get_db)
        or
        pass a db session manually to your listing service
        e.g.
        AbcListingService(read_db=sqlalchemysession)
        """
        super().__init__(msg)


class MissingExpectedAttribute(Exception):
    """Exception raised for when the user misses expected attribute."""
    pass


class FastAPIListingWarning(UserWarning):
    pass
