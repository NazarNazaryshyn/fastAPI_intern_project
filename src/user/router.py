from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPBearer
from src.user.schemas import *
from src.database import async_session
from typing import List
from src.auth.router import get_current_user
from src.user.crud import CrudMethods
from src.user.models import User


router = APIRouter()
token_auth_scheme = HTTPBearer()
db = async_session()


@router.get('/', response_model=List[UserGetSchema], status_code=status.HTTP_200_OK)
async def get_all_users(current_user: User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(session)
            return await user_crud.get_all_users()


@router.get('/{user_id}', response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(session)
            user = await user_crud.get_user_by_id(user_id)
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return user


@router.put("/{user_id}", response_model=UserUpdateSchema, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserUpdateSchema, current_user: User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(session)

            current_user = await user_crud.get_user_by_email(current_user.email)

            if current_user.id != user_id:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='you have no access')

            await user_crud.update_user(user_id, user)

            return {f"user with id {user_id} has been successfully updated"}


@router.post('/', response_model=UserGetSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema):
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(session)

            return await user_crud.create_user(user)


@router.delete("/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(session)

            current_user = await user_crud.get_user_by_email(current_user.email)

            if current_user.id != user_id:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='you have no access')

            await user_crud.delete_user(user_id)

            return {f"user with id {user_id} has been successfully deleted"}