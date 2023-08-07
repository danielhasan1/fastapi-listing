import inspect
from fastapi_listing.abstracts import AbstractFilterInterceptor, AbstractSorterInterceptor


class InterceptorObjectFactory:
    def __init__(self):
        self._interceptor = {}

    def register_interceptor(self, key: str, builder: type):
        if key is None or not key or type(key) is not str:
            raise ValueError("Invalid type key!")
        if key in self._interceptor:
            raise ValueError(f"interceptor name {key!r}, already in use with {self._interceptor[key].__name__!r}!")
        if not inspect.isclass(builder):
            raise ValueError(f"{builder!r} is not a valid class!")
        if issubclass(builder, AbstractSorterInterceptor) and not builder == AbstractSorterInterceptor:
            pass
        elif issubclass(builder, AbstractFilterInterceptor) and not builder == AbstractFilterInterceptor:
            pass
        else:
            raise ValueError("Invalid interceptor class, expects a subclass of either "
                             "'AbstractSorterInterceptor' or 'AbstractFilterInterceptor'")
        # if (not issubclass(builder, AbstractFilterInterceptor) or not issubclass(builder, AbstractSorterInterceptor)
        #         or builder == AbstractSorterInterceptor or builder == AbstractFilterInterceptor):
        #     raise ValueError("Invalid interceptor class, expects a subclass of either "
        #                      "'AbstractSorterInterceptor' or 'AbstractFilterInterceptor'")
        self._interceptor[key] = builder

    def create(self, key: str, *args, **kwargs) -> object:
        interceptor_ = self._interceptor.get(key)
        if not interceptor_:
            raise ValueError(f"interceptor factory couldn't find register key {key!r}")
        return interceptor_(*args, **kwargs)

    def aware_of(self, key: str) -> bool:
        return key in self._interceptor


interceptor_factory = InterceptorObjectFactory()
