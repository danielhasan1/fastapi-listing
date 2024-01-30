from typing import Sequence, TypeVar, Generic
import warnings
from fastapi_listing.utils import HAS_PYDANTIC, IS_PYDANTIC_V2


if HAS_PYDANTIC:
    if IS_PYDANTIC_V2:
        from pydantic import BaseModel as GenericModel, Field
    else:
        from pydantic.generics import GenericModel
        from pydantic import Field

else:
    GenericModel = object
    warnings.warn("You are using fastapi-listing without pydantic package. Avoid using any pydantic dependent features.")

T = TypeVar('T')


class BaseListingPage(GenericModel, Generic[T]):
    """Extend this to customise Page format"""
    data: Sequence[T]


class ListingPage(BaseListingPage[T], Generic[T]):
    hasNext: bool = Field(alias="hasNext")
    currentPageSize: int = Field(alias="currentPageSize")
    currentPageNumber: int = Field(alias="currentPageNumber")
    totalCount: int = Field(alias="totalCount")


class ListingPageWithoutCount(BaseListingPage[T], Generic[T]):
    hasNext: bool = Field(alias="hasNext")
    currentPageSize: int = Field(alias="currentPageSize")
    currentPageNumber: int = Field(alias="currentPageNumber")
