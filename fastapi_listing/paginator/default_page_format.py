from typing import Sequence, TypeVar, Generic
from pydantic import BaseModel, Field
import warnings

from pydantic.generics import GenericModel
from fastapi_listing.utils import HAS_PYDANTIC, IS_PYDANTIC_V2


if HAS_PYDANTIC:
    if IS_PYDANTIC_V2:
        from pydantic import BaseModel as GenericModel
    else:
        from pydantic.generics import GenericModel

else:
    GenericModel = object
    warnings.warn("You are using fastapi-listing without pydantic package. Avoid using any pydantic dependent features.")

T = TypeVar('T')


class Page(GenericModel,Generic[T]):
    data: Sequence[T]
    hasNext: bool = Field(alias="hasNext")
    currentPageSize: int = Field(alias="currentPageSize")
    currentPageNumber: int = Field(alias="currentPageNumber")
    totalCount: int = Field(alias="totalCount")
