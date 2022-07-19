from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from app.database import mappings_db
from app import models

router = APIRouter(prefix="/mappings", tags=["Mappings"])


@router.post(
    "/",
    response_model=models.MappingRead,
    response_model_by_alias=False,
    status_code=201,
)
async def mappings_create(mapping: models.Mapping):
    mapping = jsonable_encoder(mapping)
    new_mapping = await mappings_db["mappings"].insert_one(mapping)
    created_mapping = await mappings_db["mappings"].find_one(
        {"_id": new_mapping.inserted_id}
    )
    return created_mapping


@router.get(
    "/",
    response_model=models.MappingList,
    response_model_by_alias=False,
    status_code=200,
)
async def get_mappings():
    mappings = await mappings_db["mappings"].find().to_list(1000)
    print(mappings)
    return {"items": mappings}
