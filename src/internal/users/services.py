from fastapi import HTTPException, UploadFile
from firebase_admin.auth import UserRecord
from starlette import status

from pkg.celery_tools.tools import send_email_task, upload_file_task, delete_file_task
from .schema.club import CreateClub, ChangeClubImage
from .schema.profile import UserProfile, UpdateUserProfileSchema
from .schema.user import UserCreate
from ..database import db, auth as fb_auth, storage
from ..token.services import TokenService


class UserProfileService:
    user_profile_model_name = "user_profile"

    def __init__(self):
        self.db = db

    async def create_user_profile(self, data: dict, user_id: str) -> None:
        """
        Create a new document with user profile data to firebase
        :param data: validated data for user profile
        :param user_id: ...
        :return: user's profile document type Document Snapshot
        """
        validate_data = UserProfile(**data).model_dump(
            exclude_none=True,
            exclude={
                "password",
            },
            by_alias=True,
        )
        self.db.create_doc(self.user_profile_model_name, validate_data, user_id)

    async def update_user_profile(
        self, data_: UpdateUserProfileSchema, user_id: str
    ) -> dict:
        """ """

        data = data_.dict(exclude_none=True, by_alias=True)
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        self.db.update_doc(self.user_profile_model_name, user_id, data)
        return {"status": True, "message": "User profile updated", "id": user_id}

    #
    async def get_user_profile(self, user_id) -> dict:
        """ """
        profile_doc = await self.db.get_doc(self.user_profile_model_name, user_id)
        data = profile_doc.to_dict()
        return data


#
class ClubServices:
    club_model_name = "club"

    def __init__(self):
        self.db = db
        self.bucket = storage

    async def create_club(self, data: dict, user_id: str) -> None:
        """ """
        # self.db.create_doc(self.club_model_name, validated_data, user_id)
        # # validated_data['test'] = 'test'
        validate_data = CreateClub(**data).model_dump(by_alias=True)
        self.db.create_doc(self.club_model_name, validate_data, user_id)

    async def get_club_dict(self, user_id) -> dict:
        """ """
        club_dict = self.db.get_doc(self.club_model_name, user_id).to_dict()
        image_id = club_dict.get("image", None)
        if image_id:
            image = self.bucket.get_blob(f"club/{image_id}")
            club_dict["image"] = image.public_url
        return club_dict

    async def change_club_image(self, file: UploadFile, user_id: str) -> dict:
        image = ChangeClubImage(
            file=await file.read(), content_type=file.content_type, size=file.size
        )
        club_image = (
            self.db.get_doc(self.club_model_name, user_id).to_dict().get("image", None)
        )
        blob_name = f"club/{image.id}"
        if club_image:
            delete_file_task.delay(f"club/{club_image}")
        task = upload_file_task.delay(
            image.file, blob_name, image.content_type, {"id": image.id}
        )
        self.db.update_doc(self.club_model_name, user_id, {"image": image.id})
        return {"task_id": task.id}


#     def set_coach_to_club(self, data: dict, user_id: str) -> dict:
#         data['club_id'] = user_id
#         validated_data = validate(data, SetClubCoachSchema)
#         # update_doc_task.delay(self.club_model_name, user_id, validated_data)
#         return validated_data
#
#


class UserServices:

    def __init__(self):
        self.auth = fb_auth

    async def user_register(self, data: UserCreate) -> dict:
        """

        :param data:
        :return:
        """
        user = self.auth.create_user_to_firebase(data.email, data.password)
        data = data.model_dump(exclude_none=True)
        await ClubServices().create_club(data, user.uid)
        token_dict = await TokenService().create_token(user.uid)
        data["token"] = token_dict["token_doc"].get().reference
        await UserProfileService().create_user_profile(data, user.uid)
        link = self.auth.email_verification_link(user.email)
        task = send_email_task.delay(user.email, "Email Confirmation", link)
        return {"task_id": task.id}

    async def login_user(self, email: str, password: str) -> bytes:
        """ """
        user = self.auth.get_user_by_email(email)
        if not self.__check_email_verified(user):
            raise HTTPException(400, "email has not been confirmed")
        data = await self.auth.login_to_firebase(email, password)
        token = data.get("idToken", None)
        if not token:
            raise HTTPException(403, "invalid token")
        cookies = self.auth.create_cookies(token)
        return cookies

    @staticmethod
    def __check_email_verified(user: UserRecord) -> bool:
        return user.email_verified

    async def send_password_reset_link(self, email: str) -> dict:
        """
        Send letter with link to reset password to user's email_tools address
        :param: email_tools: user's email_tools
        :return: status dict
        """
        subject = "Password Reset"

        link = self.auth.password_reset_link(email)
        task = send_email_task.delay(email, subject, link)

        return {"status": True, "task_id": task.id}
