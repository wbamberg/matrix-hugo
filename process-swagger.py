# Copyright 2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Contains all the units for the spec.

This file loads swagger and JSON schema files and parses out the useful bits
and returns them as Units for use in Batesian.

For the actual conversion of data -> RST (including templates), see the sections
file instead.
"""
from collections import OrderedDict
import logging
import json
import os
import os.path
import re
import sys
import yaml
from functools import reduce

matrix_doc_dir=reduce(lambda acc,_: os.path.dirname(acc),
                      range(1, 5), os.path.abspath(__file__))

HTTP_APIS = {
    os.path.join(matrix_doc_dir, "api/application-service"): "as",
    os.path.join(matrix_doc_dir, "api/client-server"): "cs",
    os.path.join(matrix_doc_dir, "api/identity"): "is",
    os.path.join(matrix_doc_dir, "api/push-gateway"): "push",
    os.path.join(matrix_doc_dir, "api/server-server"): "ss",
}
SWAGGER_DEFINITIONS = {
    os.path.join(matrix_doc_dir, "api/application-service/definitions"): "as",
    os.path.join(matrix_doc_dir, "api/client-server/definitions"): "cs",
    os.path.join(matrix_doc_dir, "api/identity/definitions"): "is",
    os.path.join(matrix_doc_dir, "api/push-gateway/definitions"): "push",
    os.path.join(matrix_doc_dir, "api/server-server/definitions"): "ss",
}

OPERATIONS = ["get", "put", "post", "delete", "options", "head", "patch"]

logger = logging.getLogger(__name__)

# a yaml Loader which loads mappings into OrderedDicts instead of regular
# dicts, so that we preserve the ordering of properties from the api files.
#
# with thanks to http://stackoverflow.com/a/21912744/637864
class OrderedLoader(yaml.Loader):
    pass
def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    pairs = loader.construct_pairs(node)
    return OrderedDict(pairs)
OrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping)

def resolve_references(path, schema):
    if isinstance(schema, dict):
        # do $ref first
        if '$ref' in schema:
            value = schema['$ref']
            path = os.path.join(os.path.dirname(path), value)
            with open(path, encoding="utf-8") as f:
                ref = yaml.load(f, OrderedLoader)
            result = resolve_references(path, ref)
            del schema['$ref']
        else:
            result = OrderedDict()

        for key, value in schema.items():
            result[key] = resolve_references(path, value)
        return result
    elif isinstance(schema, list):
        return [resolve_references(path, value) for value in schema]
    else:
        return schema

def inherit_parents(obj):
    """
    Recurse through the 'allOf' declarations in the object
    """
    logger.debug("inherit_parents %r" % obj)

    parents = obj.get("allOf", [])
    if not parents:
        return obj

    result = {}

    # settings defined in the child take priority over the parents, so we
    # iterate through the parents first, and then overwrite with the settings
    # from the child.
    for p in list(map(inherit_parents, parents)) + [obj]:
        # child blats out type, title and description
        for key in ('type', 'title', 'description'):
            if p.get(key):
                result[key] = p[key]

        # other fields get merged
        for key in ('required', ):
            if p.get(key):
                result.setdefault(key, []).extend(p[key])

        for key in ('properties', 'additionalProperties', 'patternProperties'):
            if p.get(key):
                result.setdefault(key, OrderedDict()).update(p[key])

    return result

def get_additional_types(object, additional_types):
    this_additional_type = {
        "name": object["title"],
        "properties": []
    }
    parse_object(object, this_additional_type["properties"], additional_types)
    additional_types.append(this_additional_type)

def parse_array_items(object, additional_types):
    items = inherit_parents(object["items"])
    name = items["type"]
    if items["type"] == "object" and items.get("title") != None:
        name = items["title"]
        existing_names = map(lambda x: x["name"], additional_types)
        if not items["title"] in existing_names:
            get_additional_types(items, additional_types)
    if type(name) is list:
        name = " or ".join(name)
    return name

def parse_object(object, properties, additional_types):
    if object.get("properties") == None:
        return
    required_properties = object.get("required") or []
    for property_name in object["properties"]:
       property = object["properties"][property_name]
       property = inherit_parents(property)
       this_property = {
           "name": property_name,
           "type": property["type"],
           "description": property.get("description") or "",
           "required": property_name in required_properties
       }
       if property["type"] == "array":
           this_property["type"] = "[{array_of}]".format(array_of = parse_array_items(property, additional_types))
       properties.append(this_property)
       if this_property["type"] == "object":
           if property.get("title") != None:
               this_property["type"] = property["title"]
               # if the object doesn't have a title defined, we won't recurse into it
               existing_names = map(lambda x: x["name"], additional_types)
               if not property["title"] in existing_names:
                   get_additional_types(property, additional_types)

def parse_schema(schema, properties, additional_types):
    schema = inherit_parents(schema)
    if schema["type"] == "object":
        parse_object(schema, properties, additional_types)

## current parser does not process headers.

def parse_operation(base_path, path, operation_name, operation):
    # this is the data structure we use to represent a single operation
    # (https://swagger.io/specification/v2/#operation-object)
    operation_spec = {
        "basePath": base_path,
        "path": path,
        "summary": operation["summary"],
        "description": operation.get("description") or "",
        "method": operation_name.upper(),
        "parameters": {},
        "additional_types": [],
        "responses": [],
        "rate_limited": 429 in operation["responses"],
        "requires_auth": "security" in operation
    }
    if "parameters" in operation:
        for parameter in operation["parameters"]:
            # parameter type is given by the "in" property
            # there are 5 types: path, query, header, body, form
            # Only "body" is allowed to be a compound type (i.e. an object)
            # (https://swagger.io/specification/v2/#parameter-object)
            if parameter["in"] == "body":
                operation_spec["parameters"]["Body"] = []
                parse_schema(parameter["schema"], operation_spec["parameters"]["Body"], operation_spec["additional_types"])
            else:
                this_parameter = {
                    "name": parameter["name"],
                    "type": parameter["type"],
                    "description": parameter["description"],
                    "required": parameter.get("required") or False
                }
                if parameter["type"] == "array":
                    this_parameter["type"] = parse_array_items(parameter, operation_spec["additional_types"])
                operation_spec["parameters"][parameter["in"].capitalize()] = []
                operation_spec["parameters"][parameter["in"].capitalize()].append(this_parameter)

    for response_code in operation["responses"]:
        response = {
          "status": response_code,
          "description": operation["responses"][response_code]["description"],
          "required": operation["responses"][response_code].get("required") or False,
          "examples": operation["responses"][response_code].get("examples") or "",
          "parameters": [],
        }
        # some responses indicate "no data" by omitting `schema`, while others include an empty `schema`
        # in either case there's nothing to parse
        if operation["responses"][response_code].get("schema") and operation["responses"][response_code]["schema"].get("properties"):
            parse_schema(operation["responses"][response_code]["schema"], response["parameters"], operation_spec["additional_types"])
        operation_spec["responses"].append(response)
    return operation_spec

def process_swagger_file(filename):
    print(filename)
    operations = []
    with open(filename, "r", encoding="utf-8") as f:
        definition = yaml.load(f, OrderedLoader)
        definition = resolve_references(filename, definition)
        for path in definition["paths"]:
            for operation in OPERATIONS:
                if operation in definition["paths"][path]:
                    operations.append(parse_operation(definition["basePath"], path, operation, definition["paths"][path][operation]))
    return operations

out_dir = "data/api/client-server"

if __name__ == '__main__':
    print(matrix_doc_dir)
    specs_path = os.path.join(os.getcwd(), "api/client-server")
    dir = os.listdir(specs_path)
    for entry in dir:
        full_path = os.path.join(specs_path, entry)
        if os.path.isfile(full_path):
            operations = process_swagger_file(full_path)
            out_path = os.path.join(os.getcwd(), out_dir, entry)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(operations, indent=4, sort_keys=True))
