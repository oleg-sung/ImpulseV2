from fastapi import HTTPException
from firebase_admin import auth
from firebase_admin.auth import ExpiredSessionCookieError, InvalidSessionCookieError
from starlette.requests import Request

from internal.users.schema.user import User


async def get_current_user(request: Request) -> User:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    try:
        user = auth.verify_session_cookie(token)
        if not user.get("admin"):
            raise HTTPException(status_code=403, detail="Permission denied")
        return User(**user)
    except ExpiredSessionCookieError:
        raise HTTPException(status_code=403, detail="Token expired")
    except InvalidSessionCookieError:
        raise HTTPException(status_code=403, detail="Invalid token")
