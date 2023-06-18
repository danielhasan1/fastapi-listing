import contextlib
from contextvars import ContextVar
from typing import Optional, Callable
from contextlib import contextmanager

from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from fastapi_listing.errors import MissingSessionError

_session: ContextVar[Optional[Session]] = ContextVar("_session", default=None)

_replica_session: ContextVar[Optional[Session]] = ContextVar("_replica_session", default=None)


class DaoSessionBinderMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: ASGIApp,
            master: Optional[Session] = None,
            replica: Optional[Session] = None,
            session_close_implicit: bool = False
    ):
        super().__init__(app)
        self.close_implicit = session_close_implicit

        global _session
        global _replica_session

        self.master_token = _session.set(master)
        self.read_token = _replica_session.set(replica)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        with manager(self.read_token, self.master_token, self.close_implicit):
            response = await call_next(request)
        return response


class SessionProvider:

    @property
    def read_session(cls) -> Session:
        read_replica_session = _replica_session.get()
        if read_replica_session is None:
            raise MissingSessionError
        return read_replica_session

    @property
    def session(cls) -> Session:
        master_session = _session.get()
        if master_session is None:
            raise MissingSessionError
        return master_session


@contextmanager
def manager(t1, t2, implic_close):
    try:
        yield
    finally:
        if implic_close:
            if _session:
                _session.get().close()
            if _replica_session:
                _replica_session.get().close()
        _session.reset(t2)
        _replica_session.reset(t1)
