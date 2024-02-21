from fastapi import HTTPException
from firebase_admin import firestore
from google.cloud.firestore_v1 import DocumentReference

from .schema import CreateToken, DisableToken, Token
from ..database import db


class TokenService:
    token_model_name = "token"

    def __init__(self):
        self.db = db

    async def create_token(
        self, user_id: str
    ) -> dict[str, bool | str | DocumentReference]:
        data = {"owner_id": user_id, "club_id": user_id}
        validate_data = CreateToken(**data).model_dump(by_alias=True)
        token_doc = await self.db.create_doc(self.token_model_name, validate_data)
        return {"status": True, "token_id": token_doc.id, "token_doc": token_doc}

    async def disable_user_token(self, token: Token) -> dict:
        """ """
        validated_data = DisableToken(is_active=token.is_active).model_dump(
            by_alias=True
        )
        await self.db.update_doc(self.token_model_name, token.id, validated_data)
        return {"token_id": token.id}

    # async def get_token_info_dict(self, token_id: str) -> dict:
    #     """ """
    #     token = await self.db.get_doc(self.token_model_name, token_id)
    #     token_dict = token.to_dict()
    #     return token_dict | {"id": token.id}

    async def get_all_token_by_id(self, user_id: str) -> list:
        """ """
        tokens_query = await self.db.search_doc(
            self.token_model_name, "userCreatedID", "==", user_id
        )
        token_sort = tokens_query.order_by(
            "isActive", direction=firestore.Query.DESCENDING
        ).order_by("createdAt", direction=firestore.Query.DESCENDING)

        token_list = []
        async for token in token_sort.stream():
            token_list.append(token.to_dict() | {"id": token.id})
        return token_list

    async def delete_token_by_id(self, token: Token) -> dict:
        """ """
        if token.auth_count > 0:
            raise HTTPException(404, "token has auth count greater than 0")
        self.db.delete_doc(self.token_model_name, token.id)
        return {"status": f"token {token.id} has been deleted"}

    async def get_coach_by_tokens(self, user_id) -> dict:
        tokens_query = self.db.search_doc(
            self.token_model_name, "userCreatedID", "==", user_id
        )
        token_list = [token.reference for token in tokens_query.stream()]
        coach_query = self.db.search_doc(
            "user_profile", "token", "in", token_list
        ).where("userCreatedID", "!=", user_id)
        coach_list = [
            profile.to_dict() | {"id": profile.id} for profile in coach_query.stream()
        ]

        return {"coach": coach_list}
