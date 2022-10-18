import datetime

from fastapi import HTTPException, status
from src.database import SessionLocal
from src.models import User
from src.schemas import UserCreateSchema, UserUpdateSchema


db = SessionLocal()


class CrudMethods:

    @staticmethod
    def get_all_users(offset: int = 0, limit: int = 100):
        users = db.query(User).offset(offset).limit(limit).all()

        return users

    @staticmethod
    def get_user_by_id(given_id: int):
        user = db.query(User).filter(User.id == given_id).first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return user

    @staticmethod
    def create_user(user: UserCreateSchema):
        db_user = db.query(User).filter(User.email == user.email).first()

        if db_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        new_user = User(
            name=user.name,
            surname=user.surname,
            age=user.age,
            email=user.email,
            password=user.password
        )

        db.add(new_user)
        db.commit()

        return new_user

    @staticmethod
    def update_user(user_id: int, user: UserUpdateSchema):
        db_user = db.query(User).filter(User.id == user_id).first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        db_user.name = db_user.name if user.name is None else user.name
        db_user.surname = db_user.surname if user.surname is None else user.surname
        db_user.age = db_user.age if user.age is None else user.age
        db_user.email = db_user.email if user.email is None else user.email
        db_user.password = db_user.password if user.password is None else user.password
        db_user.updated_at = datetime.datetime.now()

        db.add(db_user)
        db.commit()

        return db_user

    @staticmethod
    def delete_user(user_id: int):
        db_user = db.query(User).filter(User.id == user_id).first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        db.delete(db_user)
        db.commit()

        return db_user


user_methods = CrudMethods()