from fastapi_listing.middlewares import SessionProvider


class DaoObjectFactory:
    def __init__(self):
        self._dao = {}

    def register_dao(self, key: str, builder):
        if key is None or not key or type(key) is not str:
            raise ValueError(f"Invalid type key, expected str type got {type(key)}!")
        if key in self._dao:
            raise ValueError(f"Dao name {key} already in use with {self._dao[key].__name__}!")
        self._dao[key] = builder

    def create(self, key, *, replica=True, master=False, both=False):
        dao_ = self._dao.get(key)
        if not dao_:
            raise ValueError(key)

        if both:
            dao_obj = dao_(read_db=SessionProvider.read_session, write_db=SessionProvider.session)

        elif master:
            dao_obj = dao_(write_db=SessionProvider.session)

        elif replica:
            dao_obj = dao_(read_db=SessionProvider.read_session)
        else:
            raise ValueError

        return dao_obj


dao_factory = DaoObjectFactory()
