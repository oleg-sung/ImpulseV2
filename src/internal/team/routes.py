from fastapi import APIRouter, Depends
from starlette import status

from internal.team.schema import Team, TeamDetails, ChangeCoach
from internal.team.services import TeamService
from internal.users.dependens import get_current_user
from internal.users.schema.profile import GetUserProfile
from internal.users.schema.user import User

router = APIRouter(prefix="/teams", tags=["Team"])


@router.get("/", response_model=list[Team], status_code=status.HTTP_200_OK)
async def get_teams(user: User = Depends(get_current_user)):
    data = await TeamService().get_teams_by_admin_id(user.uid)
    return data


@router.get(
    "/{team_id}/",
    response_model=TeamDetails,
    response_model_exclude=None,
    status_code=status.HTTP_200_OK,
)
async def get_team(team_id: str, user: User = Depends(get_current_user)):
    data = await TeamService().get_team_by_id(team_id)
    return data


@router.get(
    "/{team_id}/coach/list/",
    response_model=list[GetUserProfile],
    status_code=status.HTTP_200_OK,
)
async def get_coachs(user: User = Depends(get_current_user)):
    data = await TeamService().get_coaches(user.uid)
    return data


@router.put("/{team_id}/coach/cahnge/", status_code=status.HTTP_201_CREATED)
async def change_coache(
    team_id: str, data_: ChangeCoach, user: User = Depends(get_current_user)
):
    data = await TeamService().chenge_coach_form_team(data_.coach_id, team_id)
    return data
