import datetime

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session, selectinload

from src.company.crud import CompanyCrud
from src.company.models import Invite, Request
from src.database import async_session
from src.user.models import User
from src.user.schemas import UserCreateSchema, UserUpdateSchema

from src.auth.auth import auth_handler

from typing import List, Optional

db = async_session()


class UserCrud:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def user_admin_in(self, user_id) -> User:
        user = (await self.db_session.execute(select(User).filter(User.id == user_id).options(selectinload(User.companies_admins)))).scalars().first()

        return user

    async def user_owner_of(self, user_id) -> User:
        user = (await self.db_session.execute(select(User).filter(User.id == user_id).options(selectinload(User.companies)))).scalars().first()

        return user

    async def check_for_rights(self, company_id: int, admin_in: list, owner_of: list) -> None:
        if company_id not in admin_in:
            if company_id not in owner_of:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="you have no access to create quiz")

    async def check_for_permission(self, id_1: int, id_2: int) -> None:
        if id_1 != id_2:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail='you have no access')

    async def get_all_users(self) -> List[User]:
        users = (await self.db_session.execute(select(User))).scalars().all()

        return users

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        user = (await self.db_session.execute(select(User)
                                              .filter(User.id == user_id)))\
                                              .scalars().first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no user with id {user_id}")

        return user

    async def get_user_by_email(self, email: str) -> User:
        user = await self.db_session.execute(select(User).filter(User.email == email))

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="user with this email doesn't exist")

        return user.scalars().first()

    async def create_user(self, user: UserCreateSchema) -> User:
        db_user = (await self.db_session.execute(select(User).filter(User.email == user.email))).scalars().first()

        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="user with this email already exists")

        new_user = User(
            name=user.name,
            surname=user.surname,
            age=user.age,
            email=user.email,
            password=auth_handler.get_password_hash(user.password)
        )
        self.db_session.add(new_user)
        await self.db_session.flush()

        return new_user

    async def delete_user(self, user_id: int) -> None:
        db_user = await self.get_user_by_id(user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="user with this id doesn't exist")

        await self.db_session.execute(delete(User).filter(User.id == user_id))
        await self.db_session.commit()

    async def update_user(self, user_id: int, user: UserUpdateSchema) -> None:
        db_user = (await self.db_session.execute(select(User).filter(User.id == user_id))).scalars().first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="user with this id doesn't exist")

        if user.email is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="you are not able to change your email")

        query = (
            update(User)
            .where(User.id == user_id)
            .values(
                name=db_user.name if user.name is None else user.name,
                surname=db_user.surname if user.surname is None else user.surname,
                age=db_user.age if user.age is None else user.age,
                password=db_user.password if user.password is None else auth_handler.get_password_hash(user.password),
                updated_at=datetime.datetime.now()
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.db_session.execute(query)
        await self.db_session.flush()

    async def create_user_auth(self, email: str) -> User:
        new_user = User(
            name="",
            surname="",
            age=0,
            email=email,
            password=""
        )

        self.db_session.add(new_user)
        await self.db_session.flush()

        return new_user

    async def get_invite(self, company_id: int, current_user: User) -> Optional[Invite]:
        invite = (await self.db_session.execute(select(Invite)
                                                .filter(Invite.user_id == current_user.id,
                                                        Invite.company_id == company_id))) \
                                                .scalars().first()

        if invite is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"there is no invite from company with id {company_id}")

        return invite

    async def accept_invite(self, company_id: int, current_user: User) -> None:

        # to check whether invite from this company exists
        await self.get_invite(company_id=company_id, current_user=current_user)

        query = (
            update(Invite)
            .where(Invite.user_id == current_user.id,
                   Invite.company_id == company_id)
            .values(
                is_accepted=True
            )
            .execution_options(synchronize_session="fetch")
        )

        await self.db_session.execute(query)
        await self.db_session.flush()

    async def make_request(self, company_id: int, current_user: User) -> Request:
        company_crud_method = CompanyCrud(db_session=self.db_session)

        await company_crud_method.get_company_by_id(company_id=company_id)

        new_request = Request(user_id=current_user.id,
                              company_id=company_id,
                              is_accepted=False)

        self.db_session.add(new_request)
        await self.db_session.flush()

        return new_request
