from typing import Any, Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import jmespath
from jmespath.exceptions import ParseError
from pydantic import BaseModel, validator

app = FastAPI()


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


class Mapping(BaseModel):
    name: str
    document: MappingDocument


class MappingRead(Mapping):
    id: str


class MappingList(BaseModel):
    items: list[MappingRead]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(jsonable_encoder({"detail": exc.errors()}), status_code=400)


@app.get("/")
async def root():
    return "Data Mapper"


@app.post("/mappings", response_model=MappingRead)
async def mappings_create(mapping: Mapping):
    return mapping


@app.get("/mappings", response_model=MappingList)
async def get_mappings():
    return []


# This is a LOT just to fix 422 -> 400
# https://github.com/tiangolo/fastapi/issues/2455
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Data Mapper",
        version="0.0.1",
        description="The Data Mapper API",
        routes=app.routes,
    )
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if openapi_schema["paths"][path][method]["responses"].get("422"):
                openapi_schema["paths"][path][method]["responses"][
                    "400"
                ] = openapi_schema["paths"][path][method]["responses"]["422"]
                openapi_schema["paths"][path][method]["responses"].pop("422")
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
