try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from typing import List


class ClientSiteParamAdapter(Protocol):  # pragma: no cover - structural type only, never instantiated/called

    def get(self, key: str):
        pass
