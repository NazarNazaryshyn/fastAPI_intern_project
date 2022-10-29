from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPBearer
from src.company.crud import CompanyCrudMethods

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
async def get_all_users(current_user: User = Depends(get_current_user)) -> List[UserGetSchema]:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)
            users = await user_crud.get_all_users()
            return list(UserGetSchema(id=user.id,
                                      name=user.name,
                                      surname=user.surname,
                                      email=user.email,
                                      age=user.age) for user in users)


@router.get('/{user_id}', response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)) -> UserGetSchema:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)
            user = await user_crud.get_user_by_id(user_id=user_id)
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            return UserGetSchema(id=user.id,
                                 name=user.name,
                                 surname=user.surname,
                                 age=user.age,
                                 email=user.email)


@router.put("/{user_id}", response_model=UserUpdateSchema, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserUpdateSchema, current_user: User = Depends(get_current_user)) -> set[str]:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)

            current_user = await user_crud.get_user_by_email(email=current_user.email)

            if current_user.id != user_id:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail='you have no access')

            await user_crud.update_user(user_id=user_id, user=user)

            return {f"user with id {user_id} has been successfully updated"}


@router.post('/', response_model=UserGetSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema) -> UserGetSchema:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)
            user = await user_crud.create_user(user=user)

            return UserGetSchema(id=user.id,
                                 name=user.name,
                                 surname=user.surname,
                                 age=user.age,
                                 email=user.email)


@router.delete("/{user_id}", response_model=UserInfo)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)) -> set[str]:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)

            current_user = await user_crud.get_user_by_email(email=current_user.email)

            if current_user.id != user_id:
                raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail='you have no access')

            await user_crud.delete_user(user_id=user_id)

            return {f"user with id {user_id} has been successfully deleted"}


@router.put("/accept_invite/{company_id}")
async def accept_invite(company_id: int, current_user = Depends(get_current_user)) -> set[str]:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)
            company_crud = CompanyCrudMethods(db_session=session)
            await user_crud.accept_invite(company_id=company_id, current_user=current_user)
            await company_crud.add_user_to_employees(user_id=current_user.id, company_id=company_id)

            return {f"invite from company {company_id} was accepted"}


@router.post('/make_request/{company_id}')
async def make_request(company_id: int, current_user = Depends(get_current_user)) -> set[str]:
    async with async_session() as session:
        async with session.begin():
            user_crud = CrudMethods(db_session=session)

            return await user_crud.make_request(company_id=company_id, current_user=current_user)

