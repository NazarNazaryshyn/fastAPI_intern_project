from .database import Base
from sqlalchemy import Column, String, Integer, Date
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    age = Column(Integer)
    email = Column(String)
    password = Column(String)
    created_at = Column(Date, default=datetime.datetime.now)
    updated_at = Column(Date, onupdate=datetime.datetime.now)


