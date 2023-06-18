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
    """Excetion raised for when the user tries to access a database session before it is created."""

    def __init__(self):
        msg = """
        No session found! Either you are not currently in a request context,
        or you need to manually create a session context by using a `db` instance as
        a context manager e.g.:

        with db():
            db.session.query(User).all()
        """

        super().__init__(msg)

