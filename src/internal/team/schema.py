from pydantic import BaseModel, Field

from internal.users.schema.profile import GetUserProfile


class Team(BaseModel):
    id: str = Field(..., examples=["RsZnqWPUXYZnkNAEMT11"])
    title: str = Field(..., examples=["Team 1"])


class TeamDetails(Team):
    coach: GetUserProfile


class ChangeCoach(BaseModel):
    coach_id: str = Field(..., alias="coachID", examples=["RsZnqWPUXYZnkNAEMT11"])
