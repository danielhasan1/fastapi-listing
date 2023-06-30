from typing import List
from datetime import date

from pydantic import BaseModel, Field
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


class EmployeeListingResponse(BaseModel):
    data: List[EmployeeListDetails] = []
    currentPageSize: int
    currentPageNumber: int
    hasNext: bool
    totalCount: int
