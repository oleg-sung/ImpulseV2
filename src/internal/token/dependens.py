from fastapi import Depends

from internal.database import db
from internal.rest.errors import DocumentNotFound
from internal.token.schema import Token
from internal.users.dependens import get_current_user
from internal.users.schema.user import User


async def get_token(token_id: str, user: User = Depends(get_current_user)) -> Token:
    """
    :param token_id:
    :param user:
    :return:
    """
    token_obj = await db.get_doc("token", token_id)
    token_dict = token_obj.to_dict()
    if token_dict is None or token_dict["userCreatedID"] != user.uid:
        raise DocumentNotFound()
    token_dict.update({"id": token_id})
    return Token(**token_dict)
