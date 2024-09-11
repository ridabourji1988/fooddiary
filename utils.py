import json

def safe_json_loads(s):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return {}