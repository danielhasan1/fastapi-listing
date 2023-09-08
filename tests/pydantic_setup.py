from typing import List, Optional, Union
from datetime import date
from pydantic import BaseModel, Field
import enum

from fastapi_listing.utils import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic import computed_field
    from pydantic import ConfigDict, model_validator as validator
else:
    from pydantic import validator


class GenderEnum(enum.Enum):
    MALE = "M"
    FEMALE = "F"


class EmployeeListDetails(BaseModel):
    emp_no: int = Field(alias="empid", title="Employee ID")
    birth_date: date = Field(alias="bdt", title="Birth Date")
    first_name: str = Field(alias="fnm", title="First Name")
    last_name: str = Field(alias="lnm", title="Last Name")
    gender: GenderEnum = Field(alias="gdr", title="Gender")
    hire_date: date = Field(alias="hdt", title="Hiring Date")
    if IS_PYDANTIC_V2:
        #  model_config = {
        #     "orm_mode": True,
        #     "allow_population_by_field_name": True
        # }
        model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    else:
        class Config:
            orm_mode = True
            allow_population_by_field_name = True


class EmployeeListDetailWithCustomFields(EmployeeListDetails):
    first_name: str = Field(alias="fnm", title="First Name", exclude=True)
    last_name: str = Field(alias="lnm", title="Last Name", exclude=True)

    if IS_PYDANTIC_V2:
        @computed_field(alias="flnm")
        @property
        def full_name(self) -> str:
            # data["full_name"] = f"{data.pop('first_name')} {data.pop('last_name')}"
            full_name = ' '.join([self.first_name, self.last_name])
            return full_name

    else:
        full_name: str = Field('', alias="flnm")

        @validator('full_name', pre=True, always=True)
        def generate_full_name(cls, v, values) -> str:
            return f"{values.pop('first_name')} {values.pop('last_name')}"


class EmployeeListingResponse(BaseModel):
    data: List[EmployeeListDetails] = []
    currentPageSize: int
    currentPageNumber: int
    hasNext: bool
    totalCount: int


class EmployeeListingResponseWithCustomFields(EmployeeListingResponse):
    data: List[EmployeeListDetailWithCustomFields] = []


class DepartMentEmployeeListingDetails(BaseModel):
    first_name: str = Field(alias="fnm")
    last_name: str = Field(alias="lnm")
    dept_name: str = Field(alias="dpnm")
    from_date: date = Field(alias="frmdt")
    to_date: date = Field(alias="tdt")
    hire_date: date = Field(alias="hrdt")

    if IS_PYDANTIC_V2:
        #  model_config = {
        #     "orm_mode": True,
        #     "allow_population_by_field_name": True
        # }
        model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    else:
        class Config:
            orm_mode = True
            allow_population_by_field_name = True


class DepartMentEmployeeListingResp(BaseModel):
    data: List[DepartMentEmployeeListingDetails] = []
    currentPageSize: int
    currentPageNumber: int
    hasNext: bool
    totalCount: int


class TitledEmployeeListingDetails(BaseModel):
    emp_no: int = Field(alias="empid", title="Employee ID")
    first_name: str = Field(alias="fnm", title="First Name")
    last_name: str = Field(alias="lnm", title="Last Name")
    gender: GenderEnum = Field(alias="gdr", title="Gender")
    title: str = Field(alias="desg", title="designation")

    if IS_PYDANTIC_V2:
        #  model_config = {
        #     "orm_mode": True,
        #     "allow_population_by_field_name": True
        # }
        model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    else:
        class Config:
            orm_mode = True
            allow_population_by_field_name = True


class TitledEmployeeListingResp(BaseModel):
    data: List[TitledEmployeeListingDetails] = []
    currentPageSize: int
    currentPageNumber: int
    hasNext: bool
    totalCount: int
