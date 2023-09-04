__all__ = ['dictify_query_params']

import json
from urllib.parse import unquote
from typing import Union, List, Optional, Type


def dictify_query_params(query_param_string: str) -> Union[dict, List[dict]]:
    return json.loads(unquote(query_param_string or "") or "[]")


try:
    from pydantic import BaseModel, VERSION
    IS_PYDANTIC_V2 = VERSION.startswith("2.")
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel: Optional[Type] = None
    VERSION = ""
    IS_PYDANTIC_V2 = None
