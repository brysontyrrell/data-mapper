from fastapi import APIRouter, HTTPException

from fastapi.encoders import jsonable_encoder

from app.database import db_read_mapping
from app.mapper import Mapper
from app import models
from app.routers import PathId


router = APIRouter(prefix="/transform", tags=["Transform"])


@router.post("/{mappingId}", response_model=models.TransformOutput, status_code=200)
async def transform_data(data: models.TransformInput, mappingId: str = PathId):
    if not (mapping := await db_read_mapping(mappingId)):
        raise HTTPException(status_code=404)

    data_mapper = Mapper(mapping["document"])
    mapped_data = data_mapper.map_data(jsonable_encoder(data))

    return mapped_data
