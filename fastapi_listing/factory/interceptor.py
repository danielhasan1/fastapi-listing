import inspect


class InterceptorObjectFactory:
    def __init__(self):
        self._interceptor = {}

    def register_interceptor(self, key: str, builder: type):
        if key is None or not key or type(key) is not str:
            raise ValueError(f"Invalid type key!")
        if key in self._interceptor:
            raise ValueError(f"interceptor name: {key}, already in use with {self._interceptor[key].__name__}!")
        if not inspect.isclass(builder):
            raise ValueError(f"builder is not a valid class!")
        self._interceptor[key] = builder

    def create(self, key: str, *args, **kwargs) -> object:
        strategy_ = self._interceptor.get(key)
        if not strategy_:
            raise ValueError(key)
        return strategy_(*args, **kwargs)

    def aware_of(self, key: str) -> bool:
        return key in self._interceptor


interceptor_factory = InterceptorObjectFactory()
