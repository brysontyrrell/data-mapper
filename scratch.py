import datetime
import json
from typing import Any, Optional, Union

from bson import ObjectId

import jmespath
from jmespath.exceptions import ParseError

# from pydantic import BaseModel, ValidationError, validator
from pydantic import BaseModel as PydanticBaseModel
from pydantic import BaseConfig, root_validator, validator

input_data = {"a": 1, "b": {"c": [1, 2, 3, 4]}}


mapping_data = {
    "name": "My Mapping",
    "document": {
        "mapping": {
            "z": {"inputExpression": "a"},
            "y": {"inputExpression": "b.c[?@ > `1`] | [?@ < `4`]"},
            "x": {"stringExpression": "The last value is {var1}"},
            "w": {
                "nestedExpressions": {
                    "c1": {"inputExpression": "b.c[0]"},
                    "c2": {"inputExpression": "b.c[1]"},
                    "c3": {"constant": 1},
                },
            },
        },
        "stringExpressionValues": {"var1": "b.c[-1]"},
    },
}


class Mapper:
    def __init__(self, document: dict, **kwargs):
        self.source = document
        self._mapping = {}
        self._variables = {}

        # Compiling operations can happen at API level before persisting to database
        if "stringExpressionValues" in document:
            for k, v in document["stringExpressionValues"].items():
                self._variables[k] = jmespath.compile(v)

        self._iter_mapping(document["mapping"])

    def _iter_mapping(self, data: dict, store: dict = None):
        if store is None:
            store = self._mapping

        for k, v in data.items():
            store[k] = {}

            if "nestedExpressions" in v:
                print("NESTED-EXPRESSIONS")
                self._iter_mapping(v["nestedExpressions"], store[k])
            elif "inputExpression" in v:
                print(f"INPUT: {v}")
                store[k]["compiledExpression"] = jmespath.compile(v["inputExpression"])
            else:
                print(f"NON-INPUT: {v}")
                store[k].update(v)

    def _iter_map(self, map_: dict, output: dict, variables: dict, data: dict):
        print(map_)
        for k, v in map_.items():
            if "compiledExpression" in v:
                output[k] = v["compiledExpression"].search(data)
            elif "stringExpression" in v:
                output[k] = v["stringExpression"].format(**variables)
            elif "constant" in v:
                output[k] = v["constant"]
            else:
                output[k] = {}
                self._iter_map(v, output[k], variables, data)

    def map_data(self, data: dict):
        output_data = {}
        variables = {}

        for k, v in self._variables.items():
            variables[k] = v.search(data)

        self._iter_map(self._mapping, output_data, variables, data)
        return output_data


m = Mapper(mapping_data["document"])
# print(m._document)
# print(m._variables)
print(json.dumps(m.map_data(input_data), indent=4))


# Model Testing


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseModel(PydanticBaseModel):
    def dict(self, *args, **kwargs):
        if "exclude_unset" not in kwargs:
            kwargs["exclude_unset"] = True
        return super().dict(*args, **kwargs)

    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime.datetime: lambda dt: dt.isoformat(),
            ObjectId: str,
        }


class MappingExpression(BaseModel):
    inputExpression: Optional[str]
    stringExpression: Optional[str]
    constant: Optional[Union[str, int, float, bool]]
    nestedExpressions: Optional[dict[str, "MappingExpression"]]

    class Config:
        extra = "forbid"

    @validator("inputExpression")
    def input_expressions(cls, value: str):
        print(f"inputExpression Validation: {value}")
        try:
            jmespath.compile(value)
        except ParseError:
            raise ValueError(f"Invalid JMESPath expression: {value}")
        return value

    @root_validator(pre=True)
    def only_one_expression(cls, values):
        print(f"MappingExpression Only One: {values}")
        if len(values) > 1:
            raise ValueError("Only one expression type allowed")
        return values


class MappingDocument(BaseModel):
    mapping: dict[str, MappingExpression]
    stringExpressionValues: Optional[dict[str, str]]

    class Config:
        extra = "forbid"

    @validator("stringExpressionValues")
    def input_expressions(cls, value: dict):
        for k, v in value.items():
            try:
                jmespath.compile(v)
            except ParseError:
                raise ValueError(f"Invalid JMESPath expression: {value}")
        return value


class Mapping(BaseModel):
    name: str
    document: MappingDocument

    class Config:
        extra = "forbid"


# try:
#     m2 = Mapping(**mapping_data)
# except Exception as error:
#     print(error.json())
#     raise
