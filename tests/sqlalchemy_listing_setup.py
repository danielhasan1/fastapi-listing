"""In-memory SQLite fixture for QueryContext-layer tests that don't need the
real MySQL "employees" CI database - just a real SQLAlchemy Query underneath
SqlAlchemyQueryContext, so the op-dispatch logic runs against genuine SQLAlchemy
expressions rather than being mocked away.
"""

from datetime import date

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, Session

from fastapi_listing.dao import GenericDao

Base = declarative_base()


class Employee(Base):
    __tablename__ = "context_test_employees"

    emp_no = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    gender = Column(String(1))
    hire_date = Column(Date)


ROWS = [
    dict(emp_no=1, first_name="Sachin", last_name="Kumar", gender="M", hire_date=date(1990, 1, 1)),
    dict(emp_no=2, first_name="Rahul", last_name="Sharma", gender="M", hire_date=date(1995, 6, 15)),
    dict(emp_no=3, first_name="Anjali", last_name="Verma", gender="F", hire_date=date(2000, 3, 20)),
    dict(emp_no=4, first_name="Priya", last_name="Iyer", gender="F", hire_date=date(2005, 11, 5)),
]

_engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(_engine)
_session = Session(bind=_engine)
_session.add_all([Employee(**row) for row in ROWS])
_session.commit()


def session_factory() -> Session:
    return _session


class EmployeeDao(GenericDao):
    name = "sqlite_employee"
    model = Employee
