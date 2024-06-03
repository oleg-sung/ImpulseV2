from typing import Iterator

from fastapi import HTTPException, UploadFile
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from google.cloud.storage import Blob

from internal.collection.schema.collection import (
    DataToCreateCollection,
    CreateNewCollection,
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

    async def get_cards_info(self, q: CardType = None) -> dict:
        prefix = f"thumbnail/{self.id_collection}/"
        data = await self.bucket.get_blobs(prefix=prefix)
        result_cards_data = (
            await self.__get_cards_by_type(data, q)
            if q
            else await self.__get_cards(data)
        )
        return result_cards_data

    @staticmethod
    async def __get_cards_by_type(data: Iterator[Blob], q: str) -> dict:
        cards_dict = {}
        for card in data:
            if card.metadata["type"] == q:
                cards_dict[int(card.metadata["position"])] = card.metadata | {
                    "url": card.public_url
                }
        return cards_dict

    @staticmethod
    async def __get_cards(data: Iterator[Blob]) -> dict:
        cards_dict = {}
        for card in data:
            cards_dict[int(card.metadata["position"])] = card.metadata | {
                "url": card.public_url
            }
        return cards_dict

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

    async def create_collection(self, data: CreateNewCollection) -> dict:
        validate_data = DataToCreateCollection(**data.model_dump()).model_dump(
            by_alias=True, exclude_none=True
        ) | {"userCreatedID": self.user_id}
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

    async def get_active_collections_data(self) -> dict:
        collections_ref = await self.db.get_collection(self.collection_model_name)
        query = (
            collections_ref.where(
                filter=FieldFilter("userCreatedID", "==", self.user_id)
            )
            .where(filter=FieldFilter("status", "==", CollectionStatus.ACTIVE))
            .limit(1)
        )
        data = {}
        async for collection in query.stream():
            collection_dict = collection.to_dict()
            amound_cards = await self._get_amount_cards_for_collection(
                collection_dict["size"]
            )
            data.update(
                collection_dict | {"id": collection.id, "amoundCards": amound_cards}
            )
        if data:
            pass
        return data

    async def collection_by_status(self, status: str) -> list:
        collections_ref = await self.db.get_collection(self.collection_model_name)
        query = (
            collections_ref.where(
                filter=FieldFilter("userCreatedID", "==", self.user_id)
            )
            .where(filter=FieldFilter("status", "==", status))
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
        )
        result = []
        async for collection in query.stream():
            collection_dict = collection.to_dict()
            amound_cards = await self._get_amount_cards_for_collection(
                collection_dict["size"]
            )
            result.append(
                collection_dict | {"id": collection.id, "amoundCards": amound_cards}
            )
        return result

    async def get_all_collections_data(self) -> dict:
        """
        Getting the data for all collections
        :return: data: dict with all collections info
        """
        data = []
        collections = await self.db.get_collection(self.collection_model_name)
        query_set = (
            collections.where(filter=FieldFilter("status", "!=", "closed"))
            .where(filter=FieldFilter("userCreatedID", "==", self.user_id))
            .order_by("status")
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
        )
        async for collection in query_set.stream():
            collection_dict = collection.to_dict()
            amount_cards = await self._get_amount_cards_for_collection(
                collection_dict["size"]
            )
            data.append(
                collection_dict | {"id": collection.id, "amount_cards": amount_cards}
            )
        return {"num": len(data), "collections": data}

    @staticmethod
    async def _get_amount_cards_for_collection(size: CollectionSize) -> dict[str, int]:
        amound_cards_dict = CollectionSize.limit_cards()
        common, uncommon, rare, legendary = amound_cards_dict.get(size)
        return {
            "common": common,
            "uncommon": uncommon,
            "rare": rare,
            "legendary": legendary,
        }

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
