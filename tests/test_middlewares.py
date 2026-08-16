"""manager()'s branch logic (which combination of master/replica callables was
given, the implicit-close cleanup) is plain control flow - it only ever calls
whatever callable it's handed and stores the result in a ContextVar, so none
of this needs a real database session to exercise. Previously only covered
incidentally through the MySQL-backed tests (and only the "both" branch, at
that) - the master-only warning, replica-only, and error branches had zero
coverage even in real CI.
"""

import pytest

from fastapi_listing import middlewares
from fastapi_listing.middlewares import manager, SessionProvider
from fastapi_listing.errors import MissingSessionError


@pytest.fixture(autouse=True)
def _reset_session_context_vars():
    """_session/_replica_session are shared, module-level ContextVars -
    implicit_close=False (several tests below use it deliberately, to test
    that specific behavior) intentionally leaves them populated after the
    `with manager(...)` block exits, since that flag means "the caller
    manages session lifecycle, not manager() itself". Without this reset,
    a session left behind by one test leaks into whichever test runs next in
    the same process, regardless of test order - a test-isolation problem,
    not something manager() itself is supposed to solve."""
    middlewares._session.set(None)
    middlewares._replica_session.set(None)
    yield
    middlewares._session.set(None)
    middlewares._replica_session.set(None)


class _FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_manager_both_master_and_replica():
    master_session = _FakeSession()
    replica_session = _FakeSession()
    with manager(read_ses=lambda: replica_session, master=lambda: master_session,
                implicit_close=False, suppress_warnings=True):
        assert SessionProvider.session is master_session
        assert SessionProvider.read_session is replica_session


def test_manager_master_only_warns_and_reuses_for_read():
    session = _FakeSession()
    with pytest.warns(UserWarning, match="Only 'master' session is provided"):
        with manager(read_ses=None, master=lambda: session, implicit_close=False, suppress_warnings=False):
            assert SessionProvider.session is session
            assert SessionProvider.read_session is session


def test_manager_master_only_suppresses_warning_when_asked():
    session = _FakeSession()
    with manager(read_ses=None, master=lambda: session, implicit_close=False, suppress_warnings=True):
        assert SessionProvider.session is session


def test_manager_replica_only():
    session = _FakeSession()
    with manager(read_ses=lambda: session, master=None, implicit_close=False, suppress_warnings=True):
        assert SessionProvider.read_session is session
        with pytest.raises(MissingSessionError):
            SessionProvider.session


def test_manager_neither_raises():
    with pytest.raises(ValueError, match="Please provide either args read or master session callables"):
        with manager(read_ses=None, master=None, implicit_close=False, suppress_warnings=True):
            pass


def test_manager_implicit_close_closes_and_resets_sessions():
    master_session = _FakeSession()
    replica_session = _FakeSession()
    with manager(read_ses=lambda: replica_session, master=lambda: master_session,
                implicit_close=True, suppress_warnings=True):
        pass
    assert master_session.closed is True
    assert replica_session.closed is True
    with pytest.raises(MissingSessionError):
        SessionProvider.session
    with pytest.raises(MissingSessionError):
        SessionProvider.read_session


def test_manager_implicit_close_with_replica_only_does_not_reference_undefined_master_token():
    """The finally block's `_session.get()` guard must skip referencing
    token_master_session entirely here, since only the replica branch ran and
    only set token_read_session - a NameError would mean that guard is wrong."""
    session = _FakeSession()
    with manager(read_ses=lambda: session, master=None, implicit_close=True, suppress_warnings=True):
        pass
    assert session.closed is True


def test_manager_implicit_close_with_master_only_reuses_session_for_both_tokens():
    session = _FakeSession()
    with manager(read_ses=None, master=lambda: session, implicit_close=True, suppress_warnings=True):
        pass
    assert session.closed is True
