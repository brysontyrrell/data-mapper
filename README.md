# Data Mapper API
 
This is a small project that provides an API for creating mappings that can be applied as transformations to JSON data.

## What is a Mapping?

A mapping is a document that describes output JSON and the data from the input JSON to populate those fields. Mappings use [JMESPath](https://jmespath.org/tutorial.html) expressions allowing complex interactions with the input.

This is an example mapping:

```json
{
    "name": "My Mapping",
    "document": {
        "mapping": {
            "passA": {"inputExpression": "a"},
            "rangeC": {"inputExpression": "b.c[?@ > `1`] | [?@ < `4`]"},
            "lastC": {"stringExpression": "The last value is {var1}"},
            "anObject": {
                "nestedExpressions": {
                    "c1": {"inputExpression": "b.c[0]"},
                    "c2": {"inputExpression": "b.c[1]"},
                    "justOne": {"constant": 1}
                }
            }
        },
        "stringExpressionValues": {"var1": "b.c[-1]"}
    }
}
```

If given this input:

```json
{
  "a": "foo",
  "b": {
    "c": [1, 2, 3, 4]
  }
}
```

It will generate this output:

```json
{
    "passA": "foo",
    "rangeC": [2, 3],
    "lastC": "The last value is 4",
    "anObject": {
        "c1": 1,
        "c2": 2,
        "justOne": "1"
    }
}
```

## Mapping Expressions

Mapping are defined using a field name and a mapping expression to apply to the field's value. There are three types of mapping expressions:

* **inputExpression**
* **stringExpression**
* **constant**

To create more complex documents with nested object structures use **'nestedExpressions'** to define another level of fields mapping expressions (it is a recursive schema).

### inputExpression

These are JMESPath expressions that define the value(s) from the input JSON that will be populated into the field.

```json
{
    ...
    "mapping": {
        "passA": {"inputExpression": "a"},
        "rangeC": {"inputExpression": "b.c[?@ > `1`] | [?@ < `4`]"},
        ...
    }
}
```

In the example above the `passA` field references the value of the `a` field in the input. It and its type will be passed through without modification.

The `rangeC` field uses a more complex JMESPath expression to select values from an array that are greater than 1 but less than 4. The output will be an array of the results.

### stringExpression

A string expression is any string with variable substitution. You can define a string and then reference `stringExpressionValues` in it using `{name}` syntax. The referenced values are themselves JMESPath expressions.

```json
{
    ...
    "mapping": {
        ...
        "lastC": {"stringExpression": "The last value is {var1}"},
        ...
    },
    "stringExpressionValues": {"var1": "b.c[-1]"}
}
```

In the example above `lastC` references `var1` in the string. `var1` references the last value of the `c` array in the `b` field. You can create as complex of a string expression as you want with as many string expression values.

> An excellent use of `stringExpression` is data transformations for notifications (e.g. transforming an event into a Slack channel message payload).

### constant

A `constant` is a static value set in the output. It is not obtained from the input. A constant can be any valid JSON type or structure.

```json
{
    ...
    "mapping": {
        ...
        "anObject": {
            "nestedExpressions": {
                ...
                "justOne": {"constant": 1}
            }
        }
    }
}
```

In the above example the nested `justOne` field will always output with the value `1` as an integer.

## Getting Started

Build and launch this project using Docker:

```commandline
docker compose up --build
```

Access the API documentation at `http://localhost/docs` or `http://localhost/redoc`.

Connect directly to MongoDB at `localhost:27017` (you can use MongoDB Compass).

Create a mapping using the `/mappings` APIs and then transform data using a mapping with the `/transform` API.

## About this project

This was a learning exercise for me to get back into non-AWS stacks. They key tech I wanted to explore here was FastAPI and MongoDB. There are some comments throughout the code linking back to articles and/or GitHub issues that helped navigate some of the edge cases I encountered.

If you have suggestions, drop them in issues. This project is not meant to be a live, supported service and there is no guarantee of support if you are running it in your environment.
