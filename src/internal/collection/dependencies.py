from fastapi import HTTPException

from .schema.collection import CreateNewCollection
from ..database import db


async def cheak_collection_id(id_collection: str) -> str:
    collection = await db.get_doc("collection", id_collection)
    return collection.id


async def cheak_club_name(data: CreateNewCollection) -> CreateNewCollection:
    result = await db.search_doc("collection", "name", "==", data.name)
    if len(await result.get()):
        raise HTTPException(status_code=400, detail="Collection already exists")
    return data
