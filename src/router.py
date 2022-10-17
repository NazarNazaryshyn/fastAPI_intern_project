from typing import List
import datetime
from fastapi import APIRouter, HTTPException, status
from src.database import SessionLocal
from src.schemas import *
from src.models import *

router = APIRouter()
db = SessionLocal()


@router.get('/', response_model=List[UserGetSchema], status_code=status.HTTP_200_OK)
async def get_all_users():
    user = db.query(User).offset(0).limit(10).all()

    return user


@router.get('/{user_id}', response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return user


@router.put("/{user_id}", response_model=UserUpdateSchema, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserUpdateSchema):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db_user.name = db_user.name if user.name is None else user.name
    db_user.surname = db_user.surname if user.surname is None else user.surname
    db_user.age = db_user.age if user.age is None else user.age
    db_user.email = db_user.email if user.email is None else user.email
    db_user.password = db_user.password if user.password is None else user.password
    db_user.updated_at = datetime.datetime.now()

    db.commit()

    return {"message": f"user with id {user_id} has been updated"}


@router.post('/', response_model=UserCreateSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema):
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

    return {"message": "success!! user has been created"}


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(user)
    db.commit()

    return {"message": f"user with id {user_id} has been deleted"}
