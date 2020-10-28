from units import MatrixUnits
from units import TypeTableRow
from units import TypeTable

import json
import os

from functools import reduce

matrix_doc_dir=reduce(lambda acc,_: os.path.dirname(acc),
                      range(1, 3), os.path.abspath(__file__))

class TypeTableEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TypeTable):
            return [obj.title, obj.desc, obj._rows]
        if isinstance(obj, TypeTableRow):
            return {"title": obj.title, "key": obj.key, "desc": obj.desc, "required": obj.required}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

def dump_json(data):
    return json.dumps(data, indent=4, sort_keys=True, cls=TypeTableEncoder)

def parse_api_name(name):

    spec_code_map = {
      "cs": "client-server",
      "ss": "server-server",
      "as": "application-service",
      "is": "identity-service",
      "push": "push-gateway"
    }

    pieces = name.split("_")
    api_name = "_".join(pieces[:-1])
    spec_name = spec_code_map[pieces[-1]]
    return api_name, spec_name

m_units = MatrixUnits()

def process_apis():
    apis = m_units.load_swagger_apis()

    for key in apis:
        api_name, spec_name = parse_api_name(key)
        # identity-service does things with status code keys that breaks json.dumps
        if spec_name == "identity-service":
            continue
        dir = os.path.join(matrix_doc_dir, "data", "api", spec_name)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(os.path.join(dir, api_name + ".json"), "w", encoding="utf-8") as f:
            f.write(dump_json(apis[key]))

def process_events():
    events = m_units.load_event_schemas()
    dir = os.path.join(matrix_doc_dir, "data", "events")
    if not os.path.exists(dir):
        os.makedirs(dir)
    for event_name in events:
        with open(os.path.join(dir, event_name + ".json"), "w", encoding="utf-8") as f:
            f.write(dump_json(events[event_name]))

def process_event_examples():
    events = m_units.load_event_examples()
    dir = os.path.join(matrix_doc_dir, "data", "event-examples")
    if not os.path.exists(dir):
        os.makedirs(dir)
    for event_name in events:
        examples = []
        for example in events[event_name]:
            out = {
                "example": dump_json(example)
            }
            examples.append(out)
        with open(os.path.join(dir, event_name + ".json"), "w", encoding="utf-8") as f:
            f.write(dump_json(examples))

process_apis()
process_events()
process_event_examples()
