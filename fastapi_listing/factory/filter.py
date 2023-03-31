

class FilterObjectFactory:
    def __init__(self):
        self._filters = {}

    def register_filter(self, key, builder):
        if key in self._filters:
            raise ValueError(f"filter name already in use with {self._filters[key].__name__}!")
        self._filters[key] = builder

    def create(self, key, **kwargs):
        filter_ = self._filters.get(key)
        if not filter_:
            raise ValueError(key)
        return filter_(**kwargs)


filter_factory = FilterObjectFactory()