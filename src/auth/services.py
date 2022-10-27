from fastapi import Depends
from fastapi.security import HTTPBearer

from src.auth.auth import auth_handler
from src.auth.utils import VerifyToken
from src.database import async_session
from src.user.crud import CrudMethods

from src.user.models import User


token_auth_scheme = HTTPBearer()


def decode_token(token = Depends(auth_handler.auth_wrapper)) -> str:
    return token


def decode_auth_token(token) -> str:
    return (VerifyToken(token=token.credentials).verify())["https://example.com/email"]


async def get_current_user(token: str = Depends(token_auth_scheme)) -> User:
    try:
        email = decode_auth_token(token=token)
    except:
        valid_token = decode_token(token=token.credentials)
        email = auth_handler.decode_token(token=valid_token)

    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)

            user = await user_crud.get_user_by_email(email=email)

    if user is None:
        async with async_session() as session:
            async with session.begin():
                user_crud = CrudMethods(db_session=session)

                return await user_crud.create_user_auth(email=email)
    return user