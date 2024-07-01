from typing import Annotated

from fastapi import HTTPException, Form

from ..database import db


async def cheak_collection_id(id_collection: str) -> str:
    collection = await db.get_doc("collection", id_collection)
    return collection.id


async def cheak_club_name(name: Annotated[str, Form(max_length=200)]) -> str:
    result = await db.search_doc("collection", "name", "==", name)
    if len(await result.get()):
        raise HTTPException(status_code=400, detail="Collection already exists")
    return name
