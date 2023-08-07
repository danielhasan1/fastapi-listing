from __future__ import annotations

from typing import List, Dict, Union

from sqlalchemy import CHAR, Column, Date, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from fastapi_listing.ctyping import SqlAlchemyModel
from fastapi_listing.dao import dao_factory, GenericDao

# ------------------------------------------MODEL LAYER----------------------------------------------------------------
Base = declarative_base()
metadata = Base.metadata

t_current_dept_emp = Table(
    'current_dept_emp', metadata,
    Column('emp_no', Integer),
    Column('dept_no', CHAR(4)),
    Column('from_date', Date),
    Column('to_date', Date)
)


class Department(Base):
    __tablename__ = 'departments'

    dept_no = Column(CHAR(4), primary_key=True)
    dept_name = Column(String(40), nullable=False, unique=True)


t_dept_emp_latest_date = Table(
    'dept_emp_latest_date', metadata,
    Column('emp_no', Integer),
    Column('from_date', Date),
    Column('to_date', Date)
)


class Employee(Base):
    __tablename__ = 'employees'

    emp_no = Column(Integer, primary_key=True)
    birth_date = Column(Date, nullable=False)
    first_name = Column(String(14), nullable=False)
    last_name = Column(String(16), nullable=False)
    gender = Column(Enum('M', 'F'), nullable=False)
    hire_date = Column(Date, nullable=False)


class DeptEmp(Base):
    __tablename__ = 'dept_emp'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    dept_no = Column(ForeignKey('departments.dept_no', ondelete='CASCADE'), primary_key=True, nullable=False,
                     index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    department = relationship('Department')
    employee = relationship('Employee')


class DeptManager(Base):
    __tablename__ = 'dept_manager'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    dept_no = Column(ForeignKey('departments.dept_no', ondelete='CASCADE'), primary_key=True, nullable=False,
                     index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    department = relationship('Department')
    employee = relationship('Employee')


class Salary(Base):
    __tablename__ = 'salaries'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    salary = Column(Integer, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date, nullable=False)

    employee = relationship('Employee')


class Title(Base):
    __tablename__ = 'titles'

    emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
    title = Column(String(50), primary_key=True, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date)

    employee = relationship('Employee')


# --------------------------------------------DAO LAYER-----------------------------------------------------------------

class ClassicDao(GenericDao):  # noqa

    def create(self, values: Dict[str, Union[str, int]]) -> SqlAlchemyModel:
        pass

    def update(self, identifier: Dict[str, Union[str, int, list]], values: dict) -> bool:
        pass

    def read(self, identifier: Dict[str, Union[str, int, list]],
             fields: Union[list, str] = "__all__") -> SqlAlchemyModel:
        pass

    def delete(self, ids: List[int]) -> bool:
        pass


class TitleDao(ClassicDao):
    name = "title"
    model = Title

    def get_emp_title_by_id(self, emp_id: int) -> str:
        return self._read_db.query(self.model.title).filter(self.model.emp_no == emp_id).first().title

    def get_emp_title_by_id_from_master(self, emp_id: int) -> str:
        return self._write_db.query(self.model.title).filter(self.model.emp_no == emp_id).first().title


class SalaryDao(ClassicDao):
    name = "salary"
    model = Salary


class DeptManagerDao(ClassicDao):
    name = "deptmngr"
    model = DeptManager


class EmployeeDao(ClassicDao):
    name = "employee"
    model = Employee

    def get_emp_ids_contain_full_name(self, full_name: str) -> list[int]:
        from sqlalchemy import func
        objs = self._read_db.query(Employee.emp_no).filter(func.concat(Employee.first_name, ' ', Employee.last_name
                                                                       ).contains(full_name)).all()
        return [obj.emp_no for obj in objs]

    def get_employees_with_designations(self):
        query = self._read_db.query(Employee.emp_no, Employee.first_name, Employee.last_name, Employee.gender,
                                    Title.title).join(Title, Employee.emp_no == Title.emp_no)
        return query


class DeptEmpDao(ClassicDao):
    name = "deptemp"
    model = DeptEmp

    def get_emp_dept_mapping_base_query(self):
        query = self._read_db.query(DeptEmp.from_date, DeptEmp.to_date, Department.dept_name, Employee.first_name,
                                    Employee.last_name, Employee.hire_date
                                    ).join(Employee, DeptEmp.emp_no == Employee.emp_no
                                           ).join(Department, DeptEmp.dept_no == Department.dept_no)
        return query


class DepartmentDao(ClassicDao):
    name = "dept"
    model = Department


def register():
    dao_factory.register_dao(TitleDao.name, TitleDao)
    dao_factory.register_dao(DepartmentDao.name, DepartmentDao)
    dao_factory.register_dao(DeptEmpDao.name, DeptEmpDao)
    dao_factory.register_dao(EmployeeDao.name, EmployeeDao)
    dao_factory.register_dao(DeptManagerDao.name, DeptManagerDao)
    dao_factory.register_dao(SalaryDao.name, SalaryDao)
