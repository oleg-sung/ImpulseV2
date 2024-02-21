from typing import Iterator

from fastapi import HTTPException, UploadFile
from firebase_admin import firestore
from google.cloud.storage import Blob

from internal.collection.schema.collection import CreateCollection, DisableCollection
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

    #
    async def get_all_collections_data(self) -> dict:
        """
        Getting the data for all collections
        :return: data: dict with all collections info
        """
        data = []
        collections = await self.db.get_collection(self.collection_model_name)
        query_set = collections.order_by(
            "isActive", direction=firestore.Query.DESCENDING
        ).order_by("createdAt", direction=firestore.Query.DESCENDING)
        async for collection in query_set.stream():
            collection_dict = collection.to_dict()
            data.append(collection_dict | {"id": collection.id})
        return {"num": len(data), "collections": data}

    async def change_status_collection(self, _id: str) -> dict:
        """
        Change status of collection's active to False
        :param _id: collection's id in firebase
        :return: dict with info about updated status
        """

        collection_doc = await self.db.get_doc(self.collection_model_name, _id)
        collection_dict = collection_doc.to_dict()
        if collection_dict["userCreatedID"] != self.user_id:
            raise HTTPException(400, "Permission denied")
        validated_data = DisableCollection(**collection_dict).model_dump(
            by_alias=True,
        )
        await self.db.update_doc(self.collection_model_name, _id, validated_data)
        return {"status": True, "id": collection_doc.id}
