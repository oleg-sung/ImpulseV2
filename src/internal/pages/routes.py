from fastapi import Request, APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from internal.collection.routes import (
    get_all_collections,
    get_cards,
    get_limit_cards_in_collection,
    get_card_from_collection,
    get_collection_by_status,
    get_active_collections,
    get_close_collection,
)
from internal.collection.schema.card import CardType
from internal.team.routes import get_teams, get_team
from internal.token.routes import get_all_user_token, get_token_by_id
from internal.token.schema import Token
from internal.users.routes import get_user_profile, club_info, change_password, get_club_image

templates = Jinja2Templates(directory="src/templates")
router = APIRouter(prefix="/pages", tags=["Pages"])


@router.get("/home/", response_class=HTMLResponse)
async def home_page(
    request: Request,
    data: dict = Depends(get_all_collections),
    tokens: list = Depends(get_all_user_token),
    teams: list = Depends(get_teams),
):
    return templates.TemplateResponse(
        "frontend/main/home.html",
        {
            "request": request,
            "collections": data["collections"],
            "tokens": tokens,
            "teams": teams},
    )


@router.get("/login/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("frontend/home/login.html", {"request": request})


@router.get("/register/", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "frontend/home/registration.html", {"request": request}
    )


@router.get("/club/", response_class=HTMLResponse)
async def club_page(
    request: Request,
    club_data: dict = Depends(club_info),
    user_data: dict = Depends(get_user_profile),
):
    return templates.TemplateResponse(
        "frontend/main/club/club_page.html",
        {"request": request, "club": club_data, "user": user_data},
    )


@router.get("/profile/", response_class=HTMLResponse)
async def profile_page(request: Request, data: dict = Depends(get_user_profile)):
    if data.get("birthday", None):
        data["birthday"] = data["birthday"].strftime("%d.%m.%Y")
    return templates.TemplateResponse(
        "frontend/main/profile/profile_page.html", {"request": request, "data": data}
    )


@router.get("/collections/", response_class=HTMLResponse)
def collections_list(request: Request):
    return templates.TemplateResponse(
        "frontend/main/collections/main_collection.html",
        {"request": request},
    )


@router.get("/collections/created/", response_class=HTMLResponse)
def created_collection_page(
    request: Request,
    collection: list = Depends(get_collection_by_status),
):
    return templates.TemplateResponse(
        "frontend/main/collections/created_collection.html",
        {"request": request, "collections": collection},
    )


@router.get("/collections/active/", response_class=HTMLResponse)
def get_active_collection_page(
    request: Request,
    collection: dict = Depends(get_active_collections),
    close_collections: list = Depends(get_close_collection),
):
    return templates.TemplateResponse(
        "frontend/main/collections/get_active_collection.html",
        {
            "request": request,
            "collection": collection,
            "close_collections": close_collections,
        },
    )


@router.get("/user/profile/", response_class=HTMLResponse)
def user_profile(request: Request, profile: dict = Depends(get_user_profile)):
    return templates.TemplateResponse(
        "user/profile/user_profile.html", {"request": request, "profile": profile}
    )


@router.get("/user/profile/change/", response_class=HTMLResponse)
def change_user_password(request: Request, profile: dict = Depends(get_user_profile)):
    return templates.TemplateResponse(
        "user/profile/change_user_profile.html",
        {"request": request, "profile": profile},
    )


@router.get("/email/confirm/", response_class=HTMLResponse)
def confirm_email(request: Request, email: str = None):
    return templates.TemplateResponse(
        "user/email_confirm.html", {"request": request, "email": email}
    )


@router.get("/token/", response_class=HTMLResponse)
def token_list(request: Request, tokens: list = Depends(get_all_user_token)):
    return templates.TemplateResponse(
        "token/token_list.html", {"request": request, "tokens": tokens}
    )


@router.get("/token/{token_id}/", response_class=HTMLResponse)
def token_detail(request: Request, token: Token = Depends(get_token_by_id)):
    return templates.TemplateResponse(
        "token/detail.html",
        {"request": request, "token": token.model_dump(by_alias=True)},
    )


@router.get("/club/", response_class=HTMLResponse)
def club_detail_info(
    request: Request,
    club: dict = Depends(club_info),
):
    return templates.TemplateResponse(
        "club/detail.html",
        {"request": request, "club": club},
    )


@router.get("/club/change/motto/", response_class=HTMLResponse)
def change_club_info_page(request: Request, club: dict = Depends(club_info)):
    return templates.TemplateResponse(
        "club/change_info.html",
        {"request": request, "club": club},
    )


@router.get("/reset/password/", response_class=HTMLResponse)
def reset_password(request: Request, email: str, data: dict = Depends(change_password)):
    return templates.TemplateResponse(
        "user/reset_password.html",
        {"request": request, "data": data, "email": email},
    )


@router.get("/logout/", response_class=HTMLResponse)
def logout_app(request: Request, response: Response):
    response = templates.TemplateResponse(
        "user/logout.html",
        {"request": request},
    )
    response.delete_cookie("session")
    return response


@router.get("/collections/creates/", response_class=HTMLResponse)
def create_collection_to(request: Request):
    return templates.TemplateResponse(
        "collection/create_collection.html",
        {
            "request": request,
        },
    )


@router.get("/collections/{id_collection}/", response_class=HTMLResponse)
def collection_detail(
    request: Request,
    id_collection: str,
    limit: dict = Depends(get_limit_cards_in_collection),
):
    return templates.TemplateResponse(
        "collection/detail.html",
        {
            "request": request,
            "collection": id_collection,
            "limit": limit,
        },
    )


@router.get("/collections/{id_collection}/cards/", response_class=HTMLResponse)
def get_cards_by_type(
    request: Request,
    id_collection: str,
    q: CardType,
    data: list = Depends(get_cards),
    limit: dict = Depends(get_limit_cards_in_collection),
):

    return templates.TemplateResponse(
        "collection/card_by_type.html",
        {
            "request": request,
            "cards": data,
            "limit": limit[q],
            "id_collection": id_collection,
            "type": q.value,
        },
    )


@router.get("/collections/{id_collection}/card/create/", response_class=HTMLResponse)
def create_card(
    request: Request,
    id_collection: str,
    q: CardType,
):
    return templates.TemplateResponse(
        "collection/create_card.html",
        {
            "request": request,
            "id_collection": id_collection,
            "type": q,
        },
    )


@router.get(
    "/collections/{id_collection}/card/{id_card}/detail/", response_class=HTMLResponse
)
def card_detail(request: Request, card: dict = Depends(get_card_from_collection)):
    return templates.TemplateResponse(
        "collection/card_details.html",
        {"request": request, "card": card},
    )


@router.get("/teams/", response_class=HTMLResponse)
def get_teams(request: Request, teams: list = Depends(get_teams)):
    return templates.TemplateResponse(
        "team/team_list.html",
        {"request": request, "teams": teams},
    )


@router.get("/teams/{team_id}/", response_class=HTMLResponse)
def get_team_details(request: Request, team: dict = Depends(get_team)):
    return templates.TemplateResponse(
        "team/team_details.html",
        {"request": request, "team": team},
    )


@router.get("/cheack/", response_class=HTMLResponse)
def cheack_html(request: Request):
    return templates.TemplateResponse(
        "frontend/main/base_main.html", {"request": request}
    )
