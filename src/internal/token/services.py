from fastapi import HTTPException
from firebase_admin import firestore
from google.cloud.firestore_v1 import AsyncDocumentReference, FieldFilter

from .schema import CreateToken, DisableToken, Token
from ..database import db


class TokenService:
    token_model_name = "token"

    def __init__(self):
        self.db = db

    async def create_token(
            self, user_id: str
    ) -> dict[str, bool | str | AsyncDocumentReference]:
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

    async def get_all_token_by_id(self, user_id: str) -> list:
        """ """
        tokens_query = await self.db.search_doc(
            self.token_model_name, "userCreatedID", "==", user_id
        )
        token_sort = tokens_query.order_by(
            "isActive", direction=firestore.Query.DESCENDING
        ).order_by("date", direction=firestore.Query.DESCENDING)

        token_list = []
        async for token in token_sort.stream():
            token_list.append(token.to_dict() | {"id": token.id})
        return token_list

    async def delete_token_by_id(self, token: Token) -> dict:
        """ """
        if token.auth_count > 0:
            raise HTTPException(404, "token has auth count greater than 0")
        await self.db.delete_doc(self.token_model_name, token.id)
        return {"status": f"token {token.id} has been deleted"}

    async def get_coach_by_tokens(self, user_id: str) -> list:
        tokens_ref = await self.db.get_collection("token")
        tokens_query = tokens_ref.where(
            filter=FieldFilter("userCreatedID", "==", user_id)
        )
        token_list = [token.reference async for token in tokens_query.stream()]
        profiles_ref = await self.db.get_collection("user_profile")
        query = profiles_ref.where(filter=FieldFilter("token", "in", token_list)).where(
            filter=FieldFilter("userType", "==", "coach")
        )
        coach_list = [
            {
                "id": profile.id,
                "firstName": profile.get("firstName"),
                "lastName": profile.get("lastName"),
            }
            async for profile in query.stream()
        ]
        return coach_list

    async def get_detail_info_for_token(self, token_id: str) -> list:
        token_ref = await self.db.get_doc(self.token_model_name, token_id)
        user_profile = await self.db.get_collection("userProfile")
        user_profile_by_token = user_profile.where(
            filter=FieldFilter("token", "==", token_ref.reference)
        ).where(
            filter=FieldFilter('userType', '==', "coach")
        )
        result = []
        async for user in user_profile_by_token.stream():
            user_profile_dict = user.to_dict()
            result.append(
                {
                    "id": user.id,
                    "firstName": user_profile_dict.get("firstName"),
                    "middleName": user_profile_dict.get("middleName", None),
                    "lastName": user_profile_dict.get("lastName"),
                    "image": user_profile_dict.get("image", None),
                }
            )
        return result
