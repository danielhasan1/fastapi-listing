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
