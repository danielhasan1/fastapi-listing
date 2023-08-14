Customising your listing  query
-------------------------------

By default FastAPI Listing prepares simple queries which may look like:

``select a,b,c,d from table``

where ``a,b,c,d`` are columns that you provide either via pydantic serializer or as a list of strings.

Remember this?

``FastapiListing(self.request, self.dao, pydantic_serializer=EmployeeListindDetail).get_response(self.MetaInfo(self))``

``FastapiListing(self.request, self.dao, fields_to_fetch=['a', 'b', 'c', 'd']).get_response(self.MetaInfo(self))``

core ``class`` invokes ``get_default_read`` to prepare above mentioned vanilla query. You can easily overwrite this method
in your dao class to write your custom query.

You can either pass ``pydantic_serializer``/``fields_to_fetch`` or not as you will be writing custom ``query``.


Advanced guide for generating listing query
-------------------------------------------

Most of the time you will be writing your own custom optimised queries for retrieving listing data and it isn't unusual to write
multiple queries that gets fired on different context.

A brief example could be:

You have a system where users are grouped together in different roles. Each group of user are separated on
different layer of data levels so you need to check two thing in every listing API call

1. What role logged in user have,

2. On which data layer the user lies and show only relevant or allowed data,

To tackle this situation you may wanna write different query for each group of users.
Some queries may look simple some may look advanced some may even corporate caching layer.
This part could easily kill your listing API performance if not handled well or a small change could induce huge errors.

Going back to the topic.

As mentioned in the basics section you can create :ref:`strategies<querybasics>` encapsulating query generation logics and abstracting query preparation from rest of the code.

First Example
^^^^^^^^^^^^^

Lets say you have a dept manager table

.. code-block:: python


    class DeptManager(Base):
        __tablename__ = 'dept_manager'

        emp_no = Column(ForeignKey('employees.emp_no', ondelete='CASCADE'), primary_key=True, nullable=False)
        dept_no = Column(ForeignKey('departments.dept_no', ondelete='CASCADE'), primary_key=True, nullable=False,
                         index=True)
        from_date = Column(Date, nullable=False)
        to_date = Column(Date, nullable=False)

        department = relationship('Department')
        employee = relationship('Employee')


Whenever department managers logs into the app they should only see employees who are associated to them (engineering department manager should only see engineering staff)

Writing your own query strategy

.. code-block:: python


    from fastapi_listing.strategies import QueryStrategy
    from fastapi_listing.factory import strategy_factory


    class DepartmentWiseEmployeesQuery(QueryStrategy):

        def get_query(self, *, request: FastapiRequest = None, dao: EmployeeDao = None,
                      extra_context: dict = None) -> SqlAlchemyQuery:
            # as request and dao args are self explanatory
            # extra_context is a chained variable that can carry contextual data from one place
            # to another place. extremely helpful when passing args from router or client.
            dept_no: str = dept_no # assuming we found dept no of logged in user
            return dao.get_employees_by_dept(dept_no) # method defined in dao class

    # it is important to register your strategy with factory for use.
    strategy_factory.register("<whatever name you choose>", DepartmentWiseEmployeesQuery)

.. _dept_emp_q_stg:

Add your new listing query to employee dao

.. code-block:: python


    from sqlalchemy.orm import Query

    class EmployeeDao(ClassicDao):
        name = "employee"
        model = Employee

        def get_employees_by_dept(self, dept_no: str) -> Query:
            # assuming we have one to one mapping and we are passing manager department here
            query = self._read_db.query(self.model
                                        ).join(DeptEmp, Employee.emp_no == DeptEmp.emp_no
                                        ).filter(DeptEmp.dept_no == dept_no)
            return query


.. code-block:: python
    :emphasize-lines: 9

    @loader.register()
    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao
        query_strategy = "default_query" # strategy chosen in case runtime switch condition not satisfied
        def get_listing(self):
            if user == manager: # imaginary conditions
                self.switch("query_strategy","<whatever name we choose>") # switch strategy on the fly on object/request level

            resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
            return resp

In above example I have decided to make a switch for query strategy at runtime. So whenever a department manager logs in ``query_strategy`` will be
switched to fetch relative data and whenever other user logs in they will see global data because you have a default ``query_strategy`` placed as well. Lets call it context based switching.

Second Example
^^^^^^^^^^^^^^

1. **Different Ways to Handle Queries:**

   If you want to deal with context based switching separately, you can encapsulate logic in a single strategy class. Add instructions to generate context based queries. Inject this class into your listing service ``default_strategy = <your new strategy class>``.

.. code-block:: python

    from fastapi_listing.strategies import QueryStrategy
    from fastapi_listing.factory import strategy_factory
    from sqlalchemy.orm import Query


    class EmployeesQuery(QueryStrategy):

        def get_query(self, *, request: FastapiRequest = None, dao: EmployeeDao = None,
                      extra_context: dict = None) -> Query:
            # assuming in this scope we know about logged in user
            user = logged_in_user
            match user.role:
                case "manager" :
                    query = self.get_manager_query(user)
                    ... # you define other contexts like manager
                    ...
                    ...
                case _" : #encountering any unknown context return empty query
                    query = dao.get_empty_query() # defined in classic dao

            return query

        def get_manager_query(self, user, dao) -> Query:
            # assuming we have a way to get dept_no
            dept_no = dao.get_dept_no_via_user(user)
            return dao.get_employees_by_dept(dept_no)

    # it is important to register your strategy with factory for use.
    strategy_factory.register("<whatever name you choose for employee query class>", EmployeesQuery)

.. code-block:: python

    class EmployeeListingService(ListingService):

        default_srt_on = "Employee.emp_no"
        default_dao = EmployeeDao
        query_strategy = "<whatever name you choose for employee query class>"
        def get_listing(self):
            # if user == manager: # imaginary conditions
            #     self.switch("query_strategy","<whatever name we choose>") # switch strategy on the fly on object/request level

            # we made our query strategy class to exhibit different behaviour no need of above code
            resp = FastapiListing(self.request, self.dao).get_response(self.MetaInfo(self))
            return resp

2. **Two Approaches for Query Handling:**

   Some people might want to decide which query method to use right where the service is like we did in first example. They like to keep the way queries work separate and simple. They can use ``switch`` to easily switch between different methods.

3. **Choosing the Right Approach:**

   It's completely a users choice to make their objects behave in a certain way. FastAPI Listing is capable of adhering to users need 😍 whether you wanna keep your context based switching at service level
   or at strategy level (query strategy class) inject it in your listing service as mention in first point and make your query strategy ``object`` capable of behaving context wise.

Personally I mixes both of these when I know strategies are going to be simple I tend to make strategy objects capable of handlind different contexts but
when I know or see my single strategy class is becoming hard to maintain I tend to breakdown them to handle specefic context at a time as a result having
single responsibility objects.