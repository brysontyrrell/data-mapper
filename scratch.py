import json

import jmespath
from jmespath.exceptions import ParseError
from pydantic import BaseModel, ValidationError, validator

input_data = {"a": 1, "b": {"c": [1, 2, 3, 4]}}


mapping_data = {
    "output": {
        "z": {"inputExpression": "a"},
        "y": {"inputExpression": "b.c[?@ > `1`z] | [?@ < `4`]"},
        "x": {"stringExpression": "The last value is {var1}"},
        "w": {"c1": {"inputExpression": "b.c[0]"}, "c2": {"inputExpression": "b.c[1]"}},
    },
    "stringExpressionValues": {"var1": "b.c[-1z]"},
}


class Mapper:
    def __init__(self, mapping: dict):
        self.source = mapping
        self._output = {}
        self._variables = {}

        # Compiling operations can happen at API level before persisting to database
        if "stringExpressionValues" in mapping:
            for k, v in mapping["stringExpressionValues"].items():
                self._variables[k] = jmespath.compile(v)

        self._iter_output(self.source["output"])

    def _iter_output(self, data: dict, output: dict = None):
        if output is None:
            output = self._output

        for k, v in data.items():
            output[k] = {}

            if "inputExpression" in v:
                output[k]["compiledExpression"] = jmespath.compile(v["inputExpression"])
            elif "stringExpression" in v:
                output[k]["stringExpression"] = v["stringExpression"]
            else:
                self._iter_output(v, output[k])

    def _iter_map(self, map_: dict, output: dict, variables: dict, data: dict):
        for k, v in map_.items():
            if "compiledExpression" in v:
                output[k] = v["compiledExpression"].search(data)
            elif "stringExpression" in v:
                output[k] = v["stringExpression"].format(**variables)
            else:
                output[k] = {}
                self._iter_map(v, output[k], variables, data)

    def map_data(self, data: dict):
        output_data = {}
        variables = {}

        for k, v in self._variables.items():
            variables[k] = v.search(data)

        self._iter_map(self._output, output_data, variables, data)
        return output_data


# m = Mapper(mapping_data)

# print(json.dumps(m.map_data(input_data), indent=4))


def iterdict(d):
    for k, v in d.items():
        print(k, v)
        if isinstance(v, dict):
            yield from iterdict(v)
        else:
            yield v


def expressions_must_compile(value):
    for i in iterdict(value):
        try:
            jmespath.compile(i)
        except ParseError:
            raise ValueError(f"Invalid JMESPath expression: {i}")


class MappingDocument(BaseModel):
    output: dict[str, dict]
    stringExpressionValues: dict[str, str]

    # validators
    _output_expressions = validator("output", allow_reuse=True)(
        expressions_must_compile
    )
    _string_expressions = validator("stringExpressionValues", allow_reuse=True)(
        expressions_must_compile
    )


try:
    MappingDocument(**mapping_data)
except ValidationError as error:
    print(error.json(indent=4))
