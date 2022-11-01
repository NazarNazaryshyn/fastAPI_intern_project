from fastapi import HTTPException, APIRouter, Depends

from .auth import auth_handler
from src.database import async_session
from src.user.schemas import UserGetSchema

from src.user.crud import UserCrud
from .services import get_current_user

from src.auth.schemes import TokenScheme
from ..user.models import User

from src.company.router import get_session

auth_router = APIRouter()
db = async_session()


@auth_router.post('/login', response_model=TokenScheme)
async def login(email: str, password: str, session = Depends(get_session)) -> TokenScheme:

    user_crud = UserCrud(db_session=session)

    user = await user_crud.get_user_by_email(email=email)

    if (user is None) or (not auth_handler.verify_password(password, user.password)):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(email=user.email)

    return TokenScheme(token=token)


@auth_router.get('/me', response_model=UserGetSchema)
async def me(current_user: str = Depends(get_current_user)) -> User:

    return current_user
