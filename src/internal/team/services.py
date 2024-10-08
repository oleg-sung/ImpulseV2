from fastapi import HTTPException
from google.cloud.firestore_v1 import FieldFilter, AsyncDocumentReference

from internal.database import db


class TeamService:
    model = "team"

    def __init__(self):
        self.db = db

    async def get_teams_by_admin_id(self, admin_id: str) -> list:
        """
        Get all teams
        :param admin_id:
        :return:
        """
        teams_ref = await self.db.get_collection(self.model)
        teams_list_ref = (
            await teams_ref.where(filter=FieldFilter("clubID", "==", admin_id))
            .order_by("title")
            .get()
        )
        teams_list = []
        for team in teams_list_ref:
            team_dict = team.to_dict() | {"id": team.id}
            coach_link: AsyncDocumentReference = team.to_dict()['coach']
            coach_ref = await coach_link.get()
            coach_dict = coach_ref.to_dict()
            teams_list.append(
                team_dict | {'coach': coach_dict}
            )

        return teams_list

    async def get_team_by_id(self, team_id: str) -> dict:
        """
        Get team by
        :param team_id:
        :return:
        """
        team_ref = await self.db.get_doc(self.model, team_id)
        team_dict = team_ref.to_dict() | {"id": team_id}
        if team_dict is None:
            raise HTTPException(status_code=404, detail="Team not found")
        coach_ref = await team_dict["coach"].get()
        team_dict["coach"] = coach_ref.to_dict() | {"id": coach_ref.id}

        return team_dict

    async def get_coaches_list(self, admin_id: str, team_id: str) -> list:
        """
        Get coaches
        :param admin_id:
        :param team_id:
        :return:
        """
        team_ref = await self.db.get_doc(self.model, team_id)
        team_dict = team_ref.to_dict()
        team_coach = team_dict["coach"]
        user_profile_ref = await self.db.get_collection("userProfile")
        list_user_profile = (
            await user_profile_ref.where(filter=FieldFilter("clubID", "==", admin_id))
            .where(filter=FieldFilter("userType", "==", "coach"))
            .get()
        )
        coaches_list = []
        for user in list_user_profile:
            if user.reference != team_coach:
                user_dict = user.to_dict() | {"id": user.id}
                del user_dict['token']
                coaches_list.append(user_dict)
        return coaches_list

    async def change_coach_form_team(self, coach_id: str, team_id: str) -> dict:
        user_profile = await self.db.get_doc("userProfile", coach_id)
        if not user_profile.exists:
            raise HTTPException(status_code=404, detail="Coach not found")
        # Дообавить проверку на тип тренера!!!!!!!!
        await self.db.update_doc(self.model, team_id, {"coach": user_profile.reference})
        return {"success": True}
