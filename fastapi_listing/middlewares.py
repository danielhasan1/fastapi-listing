import contextlib
from contextvars import ContextVar, Token
from typing import Optional, Callable
from contextlib import asynccontextmanager

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
            master: Callable[[], Session] = None,
            replica: Callable[[], Session] = None,
            session_close_implicit: bool = False
    ):
        super().__init__(app)
        self.close_implicit = session_close_implicit
        self.master = master
        self.read = replica

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        async with manager(self.read(), self.master(), self.close_implicit):
            response = await call_next(request)
        return response


class SessionProviderMeta(type):

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


class SessionProvider(metaclass=SessionProviderMeta):
    pass


@asynccontextmanager
async def manager(read_ses: Session, master: Session, implicit_close):
    global _session
    global _replica_session
    token_read_session: Token = _session.set(read_ses)
    token_master_session: Token = _replica_session.set(master)
    try:
        yield
    finally:
        if implicit_close:
            if SessionProvider.session:
                _session.get().close()
            if SessionProvider.read_session:
                _replica_session.get().close()
        _session.reset(token_read_session)
        _replica_session.reset(token_master_session)
