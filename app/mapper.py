import jmespath


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
