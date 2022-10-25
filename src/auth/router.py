from fastapi import HTTPException, APIRouter, Depends
from .auth import auth_handler
from src.database import async_session
from src.user.schemas import UserGetSchema

from src.user.crud import CrudMethods
from .services import get_current_user

from src.auth.schemes import TokenScheme


auth_router = APIRouter()
db = async_session()


@auth_router.post('/login', response_model=TokenScheme)
async def login(email: str, password: str) -> str:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)
            user = await user_crud.get_user_by_email(email=email)

    if (user is None) or (not auth_handler.verify_password(password, user.password)):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(email=user.email)

    return {"token":token}


@auth_router.get('/me', response_model=UserGetSchema)
async def me(current_user: str = Depends(get_current_user)) -> UserGetSchema:

    return current_user
