import json
from collections import namedtuple


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())


# Turns json-data into a python object
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)
