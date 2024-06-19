from typing import Iterator

from fastapi import HTTPException, UploadFile
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from google.cloud.storage import Blob

from internal.collection.schema.collection import (
    DataToCreateCollection,
    ChangeStatusCollection,
    CollectionSize,
    CollectionStatus,
    CoverCreate, )
from pkg.celery_tools.tools import upload_file_task, delete_file_task, delete_list_files_task
from .schema.card import ImageCard, CardType, ChangeCardMetadata
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

    async def change_card_info(self, id_card: str, data: dict, file: UploadFile = None) -> dict:
        result = {'status': True}
        name = f"thumbnail/{self.id_collection}/{id_card}"
        blob = await self.bucket.get_blob(name)
        metadata = blob.metadata
        validate_data = ChangeCardMetadata(**data).model_dump(exclude_none=True)
        for key in validate_data.keys():
            metadata[key] = validate_data[key]
        if file.size:
            metadata.pop('id')
            delete_task = delete_file_task.delay(name)
            image = ImageCard(
                file=await file.read(),
                content_type=file.content_type,
                size=file.size,
                metadata=metadata,
            )
            metadata = image.metadata.custom_dump()
            name = f"thumbnail/{self.id_collection}/{metadata['id']}"
            task = upload_file_task.delay(image.file, name, image.content_type, metadata)
            collection = await self.db.get_doc('collection', self.id_collection)
            collection_dict = collection.to_dict()
            cards_id_list = collection_dict['cards']
            cards_id_list.remove(id_card)
            cards_id_list.append(metadata['id'])
            await self.db.update_doc('collection', self.id_collection, {"cards": cards_id_list})
            result['task_id'] = task.id
            result['delete_task'] = delete_task.id
        else:
            blob.metadata = metadata
            blob.update()

        return result


class CollectionService:
    collection_model_name = "collection"

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = db
        self.bucket = storage

    async def create_collection(self, data: dict, cover: UploadFile = None) -> dict:
        result = {}
        if cover:
            image = CoverCreate(
                file=await cover.read(),
                content_type=cover.content_type,
                size=cover.size,
            )
            data = data | {"cover": image.id}
            path = f"Collection Views/{image.id}"
            task = upload_file_task.delay(
                content=image.file,
                path=path,
                content_type=image.content_type,
            )
            result["task_id"] = task.id
        validate_data = DataToCreateCollection(**data).model_dump(
            by_alias=True, exclude_none=True
        ) | {"userCreatedID": self.user_id}
        collection_doc = await self.db.create_doc(
            self.collection_model_name, validate_data
        )
        result.update(
            {
                "status": True,
                "msg": "The collection created",
                "id": collection_doc.id,
            }
        )
        return result

    async def __upload_cover_for_collection(self):
        pass

    async def __get_cover_url(self, _id: str) -> str:
        name = f"Collection Views/{_id}"
        image = await self.bucket.get_blob(name)
        return image.public_url

    async def get_collection_data(self, _id: str) -> dict:
        collection_doc = await self.db.get_doc(self.collection_model_name, _id)
        collection_dict = collection_doc.to_dict()
        if collection_dict.get("cover", None):
            collection_dict["cover"] = await self.__get_cover_url(
                collection_dict["cover"]
            )
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
            add_data = {"id": collection.id, "amoundCards": amound_cards}
            if collection_dict.get("cover", None):
                add_data["cover"] = await self.__get_cover_url(collection_dict["cover"])
            data.update(collection_dict | add_data)

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
            if collection_dict.get("cover", None):
                collection_dict["cover"] = await self.__get_cover_url(
                    collection_dict["cover"]
                )
            result.append(
                collection_dict | {"id": collection.id, "amoundCards": amound_cards}
            )
        return result

    async def get_close_collection(self) -> list:
        collections_ref = await self.db.get_collection(self.collection_model_name)
        query = (
            collections_ref.where(
                filter=FieldFilter("userCreatedID", "==", self.user_id)
            )
            .where(filter=FieldFilter("status", "==", 'closed'))
            .order_by("createdAt", direction=firestore.Query.DESCENDING)
        )
        result = []
        async for collection in query.stream():
            collection_dict = collection.to_dict()
            result.append(collection_dict)
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
            add_data = {"id": collection.id, "amount_cards": amount_cards}
            if collection_dict.get("cover", None):
                collection_dict["cover"] = await self.__get_cover_url(
                    collection_dict["cover"]
                )
            data.append(collection_dict | add_data)
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
                    status_code=403, detail="There is already an active collection"
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
        return {"status": True, "id": collection_doc.id, 'msg': 'successful'}

    async def __get_old_covet(self, _id: str) -> str:
        collection_doc = await self.db.get_doc(self.collection_model_name, _id)
        collection_dict = collection_doc.to_dict()
        name = f"Collection Views/{collection_dict["cover"]}"
        return name

    async def change_collection_data(self, _id: str, cover: UploadFile = None, motto: str = None) -> dict:
        update_dict = {}
        result_dict = {"status": True}
        if cover and cover.size:
            old_cover = await self.__get_old_covet(_id)
            image = CoverCreate(
                file=await cover.read(),
                content_type=cover.content_type,
                size=cover.size,
            )

            update_dict["cover"] = image.id
            path = f"Collection Views/{image.id}"
            task = upload_file_task.delay(
                content=image.file,
                path=path,
                content_type=image.content_type,
            )
            delet_task = delete_file_task.delay(old_cover)
            result_dict['task_id'] = task.id
            result_dict['delet_task_id'] = delet_task.id
        if motto:
            update_dict["motto"] = motto
        await self.db.update_doc(self.collection_model_name, _id, update_dict)
        return result_dict

    async def delete_collection(self, _id: str) -> dict:
        collection_doc = await self.db.get_doc(self.collection_model_name, _id)
        collection_dict = collection_doc.to_dict()
        if (collection_dict['status'] == CollectionStatus.ACTIVE or collection_dict['status'] == CollectionStatus.CLOSED
                or collection_dict['userCreatedID'] != self.user_id):
            raise HTTPException(403, detail="Access denied")
            
        cards_list = collection_dict["cards"]
        if collection_dict.get("cover", False):
            name = f"Collection Views/{collection_dict["cover"]}"
            delete_file_task.delay(name)
        base_card_path = f"thumbnail/{_id}/"
        file_list_id = [base_card_path + cards_id for cards_id in cards_list]
        task = delete_list_files_task.delay(file_list_id)
        await self.db.delete_doc(self.collection_model_name, _id)
        return {'task_id': task.id}

