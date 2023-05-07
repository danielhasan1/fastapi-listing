import json
from urllib.parse import unquote
from typing import Union, List


def jsonify_query_params(query_param_string: str) -> Union[dict, List[dict]]:
    return json.loads(unquote(query_param_string or "") or "[]")

