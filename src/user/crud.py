import datetime

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from src.database import async_session
from src.user.models import User
from src.user.schemas import UserCreateSchema, UserUpdateSchema

from src.auth.auth import auth_handler

from typing import List
from src.user.schemas import UserGetSchema

db = async_session()


class CrudMethods:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_all_users(self) -> List[User]:
        users = (await self.db_session.execute(select(User))).scalars().all()

        return list(UserGetSchema(**{"id": user.id,
                                     "name": user.name,
                                     "surname": user.surname,
                                     "email": user.email,
                                     "age": user.age}) for user in users)

    async def get_user_by_id(self, user_id: int) -> User:
        user = (await self.db_session.execute(select(User).filter(User.id == user_id))).scalars().first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"there is no user with id {user_id}")

        return UserGetSchema(**{"id": user_id,
                                "name": user.name,
                                "surname": user.surname,
                                "email": user.email,
                                "age": user.age})

    async def get_user_by_email(self, email: str) -> User:
        user = await self.db_session.execute(select(User).filter(User.email == email))

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user with this email doesn't exist")

        return user.scalars().first()

    async def create_user(self, user: UserCreateSchema) -> User:
        db_user = (await self.db_session.execute(select(User).filter(User.email == user.email))).scalars().first()

        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user with this email already exists")

        new_user = User(
            name=user.name,
            surname=user.surname,
            age=user.age,
            email=user.email,
            password=auth_handler.get_password_hash(user.password)
        )
        self.db_session.add(new_user)
        await self.db_session.flush()

        return UserGetSchema(**{"id": new_user.id,
                                "name": new_user.name,
                                "surname": new_user.surname,
                                "email": new_user.email,
                                "age": new_user.age})

    async def delete_user(self, user_id: int) -> None:
        db_user = await self.get_user_by_id(user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        await self.db_session.execute(delete(User).filter(User.id == user_id))
        await self.db_session.commit()

    async def update_user(self, user_id: int, user: UserUpdateSchema) -> None:
        db_user = (await self.db_session.execute(select(User).filter(User.id == user_id))).scalars().first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user with this id doesn't exist")

        if user.email is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="you are not able to change your email")

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

        return UserGetSchema(**{"id": new_user.id,
                                "name": new_user.name,
                                "surname": new_user.surname,
                                "email": new_user.email,
                                "age": new_user.age})