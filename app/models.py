import datetime
from typing import Optional

from bson import ObjectId
import jmespath
from jmespath.exceptions import ParseError
from pydantic import BaseConfig, Field, validator
from pydantic import BaseModel as PydanticBaseModel

from app.utils import iterdict


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
        kwargs["exclude_unset"] = True
        return super().dict(*args, **kwargs)

    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime.datetime: lambda dt: dt.isoformat(),
            ObjectId: str,
        }


def expressions_must_compile(value):
    for i in iterdict(value):
        try:
            jmespath.compile(i)
        except ParseError:
            raise ValueError(f"Invalid JMESPath expression: {i}")
    return value


class MappingDocument(BaseModel):
    mapping: dict[str, dict]
    stringExpressionValues: Optional[dict[str, str]]

    # validators
    _mapping_expressions = validator("mapping", allow_reuse=True)(
        expressions_must_compile
    )
    _string_expressions = validator("stringExpressionValues", allow_reuse=True)(
        expressions_must_compile
    )


class Mapping(BaseModel):
    name: str
    document: MappingDocument


class MappingRead(Mapping):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class MappingList(BaseModel):
    items: list[MappingRead]
