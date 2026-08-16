"""Nothing in the existing suite actually verifies "import fastapi_listing works
without SQLAlchemy installed" - the CI's test extras always install sqlalchemy
(needed for the MySQL-backed tests), so ctyping.py's ImportError fallback path
never fires there. This was only ever checked manually, in a throwaway venv,
during development. Verified here via import-hook poisoning in a subprocess -
a real, repeatable, CI-visible check of the actual headline claim, not a
simulation that could silently stop matching reality.
"""

import subprocess
import sys

_CODE = """
import builtins
_real_import = builtins.__import__

def _blocked(name, *args, **kwargs):
    if name == "sqlalchemy" or name.startswith("sqlalchemy."):
        raise ImportError(f"simulated absence of {name}")
    return _real_import(name, *args, **kwargs)

builtins.__import__ = _blocked

import fastapi_listing
print("IMPORT_OK", fastapi_listing.__version__)
"""


def test_import_fastapi_listing_without_sqlalchemy():
    result = subprocess.run([sys.executable, "-c", _CODE], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "IMPORT_OK" in result.stdout


def test_ctyping_sqlalchemy_bound_types_are_none_without_sqlalchemy():
    code = _CODE + """
from fastapi_listing import ctyping
assert ctyping.DeclarativeMeta is None
assert ctyping.Query is None
assert ctyping.Session is None
assert ctyping.Column is None
print("CTYPING_FALLBACK_OK")
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "CTYPING_FALLBACK_OK" in result.stdout
