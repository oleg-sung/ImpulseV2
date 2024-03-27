from typing import Iterator

from fastapi import HTTPException, UploadFile
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from google.cloud.storage import Blob

from internal.collection.schema.collection import (
    CreateCollection,
    ChangeStatusCollection,
    CollectionSize,
    CollectionStatus,
)
from pkg.celery_tools.tools import upload_file_task
from .schema.card import ImageCard, CardType
from ..database import db, storage


class CardService:
    collection_model_name = "collection"

    def __init__(self, id_collection: str, user_id: str):
        self.user_id = user_id
        self.id_collection = id_collection
        self.bucket = storage
        self.db = db

    async def create_card(self, file: UploadFile, data: dict) -> dict:
        """ """
        data.update({"collection": self.id_collection})
        image = ImageCard(
            file=await file.read(),
            content_type=file.content_type,
            size=file.size,
            metadata=data,
        )
        path = f"thumbnail/{image.metadata.collection}/{image.metadata.id}"
        task = upload_file_task.delay(
            content=image.file,
            path=path,
            content_type=image.content_type,
            metadata=image.metadata.custom_dump(),
        )
        await self.db.add_doc_to_array(
            model_name=self.collection_model_name,
            key="cards",
            value=image.metadata.id,
            _id=self.id_collection,
        )
        return {"task_id": task.id}

    async def get_card_info(self, id_card: str) -> dict:
        """ """
        name = f"thumbnail/{self.id_collection}/{id_card}"
        blob = await self.bucket.get_blob(name)
        if blob is None:
            raise HTTPException(404, "Document not found")
        return blob.metadata | {"url": blob.public_url}

    async def get_cards_info(self, q: CardType = None) -> list:
        prefix = f"thumbnail/{self.id_collection}/"
        data = await self.bucket.get_blobs(prefix=prefix)
        cards_list = (
            await self.__get_cards_by_type(data, q)
            if q
            else await self.__get_cards(data)
        )
        return cards_list

    @staticmethod
    async def __get_cards_by_type(data: Iterator[Blob], q: str) -> list:
        cards_list = [
            i.metadata | {"url": i.public_url} for i in data if i.metadata["type"] == q
        ]
        return cards_list

    @staticmethod
    async def __get_cards(data: Iterator[Blob]) -> list:
        cards_list = [i.metadata | {"url": i.public_url} for i in data]
        return cards_list

    async def get_limit(self) -> dict:
        collection_data = await self.db.get_doc(
            self.collection_model_name, self.id_collection
        )
        collection_dict = collection_data.to_dict()
        common_limit, uncommon_limit, rare_limit, legendary_limit = (
            CollectionSize.limit_cards()[collection_dict["size"]]
        )
        prefix = f"thumbnail/{self.id_collection}/"
        data = await self.bucket.get_blobs(prefix=prefix)
        limit_dict = {
            "common": common_limit,
            "uncommon": uncommon_limit,
            "rare": rare_limit,
            "legendary": legendary_limit,
        }
        for blob in data:
            cards_type = blob.metadata["type"]
            limit_dict[cards_type] -= 1
        return limit_dict


class CollectionService:
    collection_model_name = "collection"

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = db

    async def create_collection(self, data: CreateCollection) -> dict:
        validate_data = data.model_dump(by_alias=True, exclude_none=True) | {
            "userCreatedID": self.user_id
        }
        collection_doc = await self.db.create_doc(
            self.collection_model_name, validate_data
        )
        return {
            "status": True,
            "msg": "The collection created",
            "id": collection_doc.id,
        }

    async def get_collection_data(self, _id: str) -> dict:
        collection_doc = await self.db.get_doc(self.collection_model_name, _id)
        collection_dict = collection_doc.to_dict()
        return collection_dict | {"id": collection_doc.id}

    async def get_closed_collection(self): ...

    async def get_all_collections_data(self) -> dict:
        """
        Getting the data for all collections
        :return: data: dict with all collections info
        """
        data = []
        collections = await self.db.get_collection(self.collection_model_name)
        query_set = (
            collections.where(filter=FieldFilter("status", "!=", "closed"))
            .order_by("status")
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
        )
        async for collection in query_set.stream():
            collection_dict = collection.to_dict()
            data.append(collection_dict | {"id": collection.id})
        return {"num": len(data), "collections": data}

    async def change_status_collection(
        self, _id: str, status: CollectionStatus
    ) -> dict:
        """

        :param _id:
        :param status:
        :return:
        """
        collection_doc = await self.db.get_doc(self.collection_model_name, _id)
        collection_dict = collection_doc.to_dict()
        if status == CollectionStatus.ACTIVE:
            collections = await self.db.get_collection(self.collection_model_name)
            query = collections.where(
                filter=FieldFilter("userCreatedID", "==", self.user_id)
            ).where(filter=FieldFilter("status", "==", status))
            result = await query.get()
            if result:
                raise HTTPException(
                    status_code=403, detail="Уже есть активная коллекция"
                )
            size = CollectionSize.get_size_dict(collection_dict["size"])
            if len(collection_dict["cards"]) < size:
                raise HTTPException(403, detail="Collection is not full")

        collection_dict.update({"status": status})
        if collection_dict["userCreatedID"] != self.user_id:
            raise HTTPException(403, "Permission denied")
        validated_data = ChangeStatusCollection(**collection_dict).model_dump(
            by_alias=True,
        )
        await self.db.update_doc(self.collection_model_name, _id, validated_data)
        return {"status": True, "id": collection_doc.id}
