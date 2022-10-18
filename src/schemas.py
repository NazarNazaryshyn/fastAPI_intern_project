from typing import Optional, List
from pydantic import BaseModel
from src.models import User


class UserCreateSchema(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    age: Optional[int]
    email: str
    password: str

    class Config:
        orm_mode = True


class UserGetSchema(BaseModel):
    id: int
    name: str
    surname: str
    age: int
    email: str

    class Config:
        orm_mode = True


class UserUpdateSchema(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    age: Optional[int]
    email: Optional[str]
    password: Optional[str]

    class Config:
        orm_mode = True


class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
