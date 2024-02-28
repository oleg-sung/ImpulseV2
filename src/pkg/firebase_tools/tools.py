import base64
import io
import json
from datetime import timedelta
from typing import Any, Iterator

import firebase_admin
import requests
from fastapi import HTTPException
from firebase_admin import credentials, firestore, auth, storage, firestore_async
from firebase_admin.auth import UserRecord, UserNotFoundError
from google.cloud.firestore_v1 import (
    DocumentSnapshot,
    Client,
    ArrayUnion,
    AsyncClient,
    AsyncCollectionReference,
    AsyncDocumentReference,
    AsyncQuery,
)
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.types import WriteResult
from google.cloud.storage import Bucket, Blob

from configuration.config import settings


class FirebaseTools:

    def __init__(self, conf: str = settings.CRED_PATH):
        self.__cred = credentials.Certificate(conf)
        self.options_dict = {
            "storageBucket": settings.FB_BUCKET,
            "databaseURL": settings.FB_URL,
        }
        try:
            self.app = firebase_admin.initialize_app(
                self.__cred, options=self.options_dict
            )
        except ValueError:
            self.app = firebase_admin.get_app()

    @staticmethod
    def get_current_app() -> firebase_admin.App:
        return firebase_admin.get_app()

    @staticmethod
    def get_firebase_client() -> Client:
        return firestore.client()

    @staticmethod
    def get_storage_client() -> Bucket:
        return storage.bucket()

    @staticmethod
    def get_asunc_firebase_client() -> AsyncClient:
        return firestore_async.client()


class FirebaseAuthTools:

    def create_user_to_firebase(self, email: str, password: str) -> UserRecord:
        """
        Create a new user to firebase
        :param email: user's email_tools address
        :param password: user's password
        :return: user objects
        """
        try:
            user = auth.create_user(email=email, password=password)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        self.set_claims(user.uid, admin=True)
        return user

    @staticmethod
    async def login_to_firebase(
        email: str, password: str, return_secure_token: bool = True
    ) -> dict:
        """ """
        payload = json.dumps(
            {
                "email": email,
                "password": password,
                "return_secure_token": return_secure_token,
            }
        )
        api_key = settings.FB_API_KEY
        rest_api_url = (
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        )

        r = requests.post(rest_api_url, params={"key": api_key}, data=payload)

        return r.json()

    @staticmethod
    def get_user_by_email(email: str) -> UserRecord:
        """
        Get user info by email_tools and return
        :param email: user's email_tools
        :return: object with user info
        """
        try:
            return auth.get_user_by_email(email)
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    def create_cookies(token, time=None) -> bytes:
        """ """
        cookies = auth.create_session_cookie(
            token, timedelta(seconds=1209600) if time is None else time
        )
        return cookies

    @staticmethod
    def set_claims(uid, **kwargs) -> None:
        auth.set_custom_user_claims(uid, {**kwargs})

    @staticmethod
    def email_verification_link(email: str) -> str:
        return auth.generate_email_verification_link(email)

    @staticmethod
    def password_reset_link(email: str) -> str:
        return auth.generate_password_reset_link(email)


class FirebaseStorage:
    def __init__(self):
        self.bucket = storage.bucket()

    def create_blob(
        self, path: str, metadata: dict = None, content_type: str = None
    ) -> Blob:
        blob = self.bucket.blob(path)
        blob.metadata = metadata
        blob.content_type = content_type
        return blob

    async def get_blob(self, name: str) -> Blob:
        return self.bucket.get_blob(name)

    async def get_blobs(self, prefix: str) -> Iterator[Blob]:
        blobs = self.bucket.list_blobs(prefix=prefix)
        return blobs

    def upload_file_to_storage(
        self, content: str, path: str, content_type: None, metadata: dict = None
    ) -> None:
        decoded_image = base64.b64decode(content)
        _content = io.BytesIO(decoded_image)
        blob = self.create_blob(path, metadata, content_type)
        blob.upload_from_file(_content)
        blob.make_public()


class FirebaseAsunc:
    def __init__(self):
        self.db = firestore_async.client()

    async def get_collection(self, name: str) -> AsyncCollectionReference:
        return self.db.collection(name)

    async def get_doc(self, model: str, _id: str) -> DocumentSnapshot:
        doc = await self.db.collection(model).document(_id).get()
        # if not doc.exists:
        #     raise HTTPException(status_code=404, detail="Document not found")
        return doc

    async def create_doc(
        self, model_name, data: dict, _id: str = None
    ) -> AsyncDocumentReference:
        """

        :param model_name:
        :param data:
        :param _id:
        :return:
        """
        doc = self.db.collection(model_name).document(_id)
        await doc.set(data)
        return doc

    async def update_doc(self, model_name: str, _id: str, data: dict) -> None:
        doc = self.db.collection(model_name).document(_id)
        await doc.update(data)

    async def delete_doc(self, model_name: str, _id: str) -> None:
        doc = self.db.collection(model_name).document(_id)
        await doc.delete()

    async def search_doc(
        self, model_name: str, fields: str, op: str, value: str | int | bool | list
    ) -> AsyncQuery:
        query = self.db.collection(model_name).where(
            filter=FieldFilter(field_path=fields, op_string=op, value=value)
        )
        return query

    async def add_doc_to_array(
        self, model_name: str, key: str, value: Any, _id: str = None
    ) -> WriteResult:
        doc = self.db.collection(model_name).document(_id)
        add_dict = {key: ArrayUnion([value])}
        result = await doc.update(add_dict)
        return result
