from typing import List

from fastapi import APIRouter, HTTPException, status
from .database import SessionLocal
from src.schemas import *
from src.models import *

router = APIRouter()
db = SessionLocal()


@router.get('/', response_model=List[UserGetSchema], status_code=status.HTTP_200_OK)
async def get_all_users():
    user = db.query(User).all()

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
    db_user.name = user.name
    db_user.surname = user.surname
    db_user.age = user.age
    db_user.email = user.email
    db_user.password = user.password

    db.commit()

    return db_user


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

    return new_user


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(user)
    db.commit()

    return user