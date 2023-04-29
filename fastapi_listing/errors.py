class FastapiListingError(BaseException):
    pass


class ListingFilterError(FastapiListingError):
    pass


class ListingSorterError(FastapiListingError):
    pass


class ListingPaginatorError(FastapiListingError):
    pass
