import inspect

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


class FastapiListingMigrationError(FastapiListingError):
    """Raised when code written against the pre-0.4.0 raw-SQLAlchemy-Query
    contract (Filter/Sorter methods keyed on 'query=', custom QueryStrategy
    returning a bare Query) is run against 0.4.0+, instead of letting it fail
    with a bare, unhelpful TypeError/AttributeError."""

    def __init__(self, message: str):
        super().__init__(
            f"{message}\n"
            "fastapi-listing 0.4.0 replaced the raw SQLAlchemy Query threaded through "
            "Filter/Sorter/QueryStrategy/Paginator with a backend-agnostic QueryContext. "
            "See docs/query.rst and docs/filters.rst for the migration."
        )


def guard_legacy_signature(bound_method, *, legacy_kwarg: str, new_kwarg: str, subject: str, fix: str) -> None:
    """Proactively detect a pre-0.4.0 method signature (still keyed on the old
    kwarg name) before calling it, so the failure is a clear
    FastapiListingMigrationError instead of a bare TypeError raised mid-call
    (which would be indistinguishable from an unrelated bug in the method)."""
    try:
        params = inspect.signature(bound_method).parameters
    except (TypeError, ValueError):
        return
    if new_kwarg not in params and legacy_kwarg in params:
        raise FastapiListingMigrationError(f"{subject} still uses the pre-0.4.0 {legacy_kwarg!r} parameter. {fix}")
