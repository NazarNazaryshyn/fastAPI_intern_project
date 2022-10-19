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


def decode_token(token):
    # if len(token) < 165:
    #     decoded = auth_handler.decode_token(token)
    #     return decoded

    try:
        decoded = VerifyToken(token.credentials).verify()
        return decoded['https://example.com/email']
    except:
        decoded = auth_handler.decode_token(token)
        return decoded


def current_user(token: str = Depends(token_auth_scheme)):
    decoded_email = decode_token(token)

    user = db.query(User).filter(User.email == decoded_email).first()

    if user is None:
        new_user = user_methods.create_user_for_auth(decoded_email)
        return new_user

    return user


@auth_router.get('/me', response_model=UserGetSchema)
async def me(current_user: str = Depends(current_user)):

    return current_user



