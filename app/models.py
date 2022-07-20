import datetime
from typing import Optional, Union

from bson import ObjectId
import jmespath
from jmespath.exceptions import ParseError
from pydantic import BaseConfig, Field, root_validator, validator
from pydantic import BaseModel as PydanticBaseModel


# `PyObjectId` and `BaseModel` adopted from this GitHub issue:
# https://github.com/tiangolo/fastapi/issues/1515
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


# Fix API docs showing "_id" and not "id"
# https://github.com/tiangolo/fastapi/issues/1515#issuecomment-1072526469
def _mongo_id_mutator(cls, values) -> dict:
    if "_id" in values:
        values["id"] = values["_id"]
        del values["_id"]
    return values


def mongo_id_mutator() -> classmethod:
    decorator = root_validator(pre=True, allow_reuse=True)
    validation = decorator(_mongo_id_mutator)
    return validation


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


class MappingRead(Mapping):
    id: PyObjectId = Field(default_factory=PyObjectId)

    _id_validator: classmethod = mongo_id_mutator()


class MappingList(BaseModel):
    items: list[MappingRead]
