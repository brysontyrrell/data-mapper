from fastapi import APIRouter, HTTPException

from fastapi.encoders import jsonable_encoder

from app.database import (
    db_create_mapping,
    db_delete_mapping,
    db_read_mapping,
    db_list_mappings,
    db_update_mapping,
    db_update_mapping_patch,
)
from app import models
from app.routers import PathId

router = APIRouter(prefix="/mappings", tags=["Mappings"])


@router.get(
    "/",
    response_model=models.MappingListResponse,
    response_model_by_alias=False,
    status_code=200,
)
async def list_mappings():
    mappings = await db_list_mappings()
    return {"items": mappings}


@router.post(
    "/",
    response_model=models.MappingResponse,
    response_model_by_alias=False,
    status_code=201,
)
async def create_mapping(mapping: models.Mapping):
    created_mapping = await db_create_mapping(jsonable_encoder(mapping))
    return created_mapping


@router.get(
    "/{mappingId}",
    response_model=models.MappingResponse,
    response_model_by_alias=False,
    status_code=200,
)
async def read_mapping(mappingId: str = PathId):
    if not (mapping := await db_read_mapping(mappingId)):
        raise HTTPException(status_code=404)

    return mapping


@router.put(
    "/{mappingId}",
    response_model=models.MappingResponse,
    response_model_by_alias=False,
    status_code=200,
)
async def update_student(*, mappingId: str = PathId, mapping: models.Mapping):
    # mapping = mapping.dict(exclude_none=True)
    mapping_update = {k: v for k, v in mapping.dict().items() if v is not None}

    if not (updated_mapping := await db_update_mapping(mappingId, mapping_update)):
        raise HTTPException(status_code=404)

    return updated_mapping


@router.patch(
    "/{mappingId}",
    response_model=models.MappingResponse,
    response_model_by_alias=False,
    status_code=200,
)
async def update_patch_student(*, mappingId: str = PathId, mapping: models.Mapping):
    if not (
        updated_mapping := await db_update_mapping_patch(
            mappingId, jsonable_encoder(mapping)
        )
    ):
        raise HTTPException(status_code=404)

    return updated_mapping


@router.delete("/{mappingId}", status_code=204)
async def delete_mapping(mappingId: str = PathId):
    if not await db_delete_mapping(mappingId):
        raise HTTPException(status_code=404)
