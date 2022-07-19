import os

from bson import ObjectId
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
mappings_db = client.mappings


async def db_create_mapping(item: dict):
    new = await mappings_db["mappings"].insert_one(item)
    return await mappings_db["mappings"].find_one({"_id": new.inserted_id})


async def db_read_mapping(id_: str):
    return await mappings_db["mappings"].find_one({"_id": ObjectId(id_)})


async def db_list_mappings():
    # TODO: Pagination
    return await mappings_db["mappings"].find().to_list(1000)


async def db_update_mapping(id_: str, item: dict):
    # This code behaves exactly as a PUT operation.
    # Need pre-fetch merge logic for PATCH!
    id_ = ObjectId(id_)

    if len(item) >= 1:
        update_result = await mappings_db["mappings"].update_one(
            {"_id": id_}, {"$set": item}
        )
        if update_result.modified_count != 1:
            raise Exception  # Future error here

    return await mappings_db["mappings"].find_one({"_id": id_})


async def db_delete_mapping(id_: str):
    delete_result = await mappings_db["mappings"].delete_one({"_id": ObjectId(id_)})
    print(delete_result)
    if delete_result.deleted_count != 1:
        return False

    return True
