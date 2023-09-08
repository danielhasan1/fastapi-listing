__all__ = ['DaoSessionBinderMiddleware']

from contextvars import ContextVar, Token
from typing import Optional, Callable
from contextlib import contextmanager
from warnings import warn

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
            app: ASGIApp, *,
            master: Callable[[], Session] = None,
            replica: Callable[[], Session] = None,
            session_close_implicit: bool = False,
            suppress_warnings: bool = False,
    ):
        super().__init__(app)
        self.close_implicit = session_close_implicit
        self.master = master
        self.read = replica
        self.suppress_warnings = suppress_warnings

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # TODO: lazy sessions
        with manager(self.read, self.master, self.close_implicit, self.suppress_warnings):
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


@contextmanager
def manager(read_ses: Callable[[], Session], master: Callable[[], Session], implicit_close: bool,
            suppress_warnings: bool):
    global _session
    global _replica_session
    if read_ses and master:
        token_read_session: Token = _replica_session.set(read_ses())
        token_master_session: Token = _session.set(master())
    elif master:
        sess = master()
        token_read_session: Token = _replica_session.set(sess)
        token_master_session: Token = _session.set(sess)
        if not suppress_warnings:
            warn("Only 'master' session is provided. dao will use master for read executes."
                 "To suppress this warning add 'suppress_warnings=True'")
    elif read_ses:
        token_read_session: Token = _replica_session.set(read_ses())
    else:
        raise ValueError("Error with DaoSessionBinderMiddleware! "
                         "Please provide either args read or master session callables.")
    try:
        yield
    finally:
        if implicit_close:
            if _session.get():
                _session.get().close()
                _session.reset(token_master_session)  # type: ignore # noqa: F823
            if _replica_session.get():
                _replica_session.get().close()
                _replica_session.reset(token_read_session)  # type: ignore # noqa: F823
