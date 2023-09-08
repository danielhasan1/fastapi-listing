try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

from typing import List


class ClientSiteParamAdapter(Protocol):

    def get(self, key: str):
        pass
