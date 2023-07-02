from typing import List, Optional, Union
from datetime import date

from pydantic import BaseModel, Field, validator
import enum


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

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class EmployeeListDetailWithCustomFields(EmployeeListDetails):
    full_name: str = Field('', alias="flnm", title="Full Name")

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
