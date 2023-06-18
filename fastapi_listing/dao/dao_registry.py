from fastapi_listing.middlewares import SessionProvider


class DaoObjectFactory:
    def __init__(self):
        self._dao = {}

    def register_dao(self, key: str, builder):
        if key is None or not key:
            raise ValueError(f"Invalid type key!")
        if key in self._dao:
            raise ValueError(f"filter name already in use with {self._dao[key].__name__}!")
        self._dao[key] = builder

    def create(self, key, *, replica=False, master=True, both=False):
        dao_ = self._dao.get(key)
        if not dao_:
            raise ValueError(key)

        if both:
            dao_(read_db=SessionProvider.read_session, write_db=SessionProvider.session)

        elif master:
            dao_(read_db=SessionProvider.session, write_db=SessionProvider.session)

        elif replica:
            dao_(read_db=SessionProvider.read_session)


dao_factory = DaoObjectFactory()
