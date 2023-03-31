import json
from urllib.parse import unquote


def jsonify_query_params(query_param_string: str) -> dict | list[dict]:
    return json.loads(unquote(query_param_string or "") or "[]")
