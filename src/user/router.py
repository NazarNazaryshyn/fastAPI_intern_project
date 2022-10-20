from fastapi import APIRouter, status, Depends
from fastapi.security import HTTPBearer
from src.user.schemas import *
from src.user.crud import user_methods
from src.database import SessionLocal
from typing import List
from src.auth.router import get_current_user

router = APIRouter()
token_auth_scheme = HTTPBearer()
db = SessionLocal()



@router.get('/', response_model=List[UserGetSchema], status_code=status.HTTP_200_OK)
async def get_all_users(current_user: str = Depends(get_current_user)):
    users = user_methods.get_all_users(offset=0, limit=10)

    return users


@router.get('/{user_id}', response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, current_user: str = Depends(get_current_user)):
    user = user_methods.get_user_by_id(user_id)

    return user


@router.put("/{user_id}", response_model=UserUpdateSchema, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserUpdateSchema, current_user: str = Depends(get_current_user)):
    updated_user = user_methods.update_user(user_id, user)

    return updated_user


@router.post('/', response_model=UserCreateSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema):
    new_user = user_methods.create_user(user)

    return new_user


@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: str = Depends(get_current_user)):
    deleted_user = user_methods.delete_user(user_id)

    return deleted_user
