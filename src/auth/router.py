from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import HTTPBearer

from .auth import auth_handler
from src.database import SessionLocal
from src.user.models import User
from src.auth.utils import VerifyToken
from src.user.schemas import UserGetSchema
from src.user.crud import user_methods

auth_router = APIRouter()
db = SessionLocal()
token_auth_scheme = HTTPBearer()


@auth_router.post('/login')
def login(email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if (user is None) or (not auth_handler.verify_password(password, user.password)):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user.email)

    return {"token": token}


def decode_token(token = Depends(auth_handler.auth_wrapper)):
    return token


def decode_auth_token(token):
    return (VerifyToken(token.credentials).verify())['https://example.com/email']


def get_current_user(token: str = Depends(token_auth_scheme)):
    if len(token.credentials) == 141:
        valid_token = decode_token(token.credentials)
        email = auth_handler.decode_token(valid_token)
    else:
        email = decode_auth_token(token)

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        new_user = user_methods.create_user_for_auth(email)
        return new_user

    return user


@auth_router.get('/me', response_model=UserGetSchema)
async def me(current_user: str = Depends(get_current_user)):

    return current_user



