from fastapi import APIRouter, HTTPException, Path

from fastapi.encoders import jsonable_encoder

from app.database import (
    db_create_mapping,
    db_delete_mapping,
    db_read_mapping,
    db_list_mappings,
    db_update_mapping,
)
from app import models

PathId = Path(regex=r"^[0-9a-f]{24}$")

router = APIRouter(prefix="/mappings", tags=["Mappings"])


@router.get(
    "/",
    response_model=models.MappingList,
    response_model_by_alias=False,
    status_code=200,
)
async def list_mappings():
    mappings = await db_list_mappings()
    return {"items": mappings}


@router.post(
    "/",
    response_model=models.MappingRead,
    response_model_by_alias=False,
    status_code=201,
)
async def create_mapping(mapping: models.Mapping):
    mapping = jsonable_encoder(mapping)
    created_mapping = await db_create_mapping(mapping)
    return created_mapping


@router.get(
    "/{id}",
    response_model=models.MappingRead,
    response_model_by_alias=False,
    status_code=200,
)
async def read_mapping(id: str = PathId):
    if not (mapping := await db_read_mapping(id)):
        raise HTTPException(status_code=404)

    return mapping


@router.put(
    "/{id}",
    response_model=models.MappingRead,
    response_model_by_alias=False,
    status_code=200,
)
async def update_student(*, id: str = PathId, mapping: models.Mapping):
    # mapping = mapping.dict(exclude_none=True)
    mapping_update = {k: v for k, v in mapping.dict().items() if v is not None}

    if not (updated_mapping := await db_update_mapping(id, mapping_update)):
        raise HTTPException(status_code=404)

    return updated_mapping


@router.delete("/{id}", status_code=204)
async def delete_mapping(id: str = PathId):
    if not await db_delete_mapping(id):
        raise HTTPException(status_code=404)
