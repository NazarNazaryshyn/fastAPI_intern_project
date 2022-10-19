from src.database import Base
from sqlalchemy import Column, String, Integer, Date
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(Date, default=datetime.datetime.now, nullable=False)
    updated_at = Column(Date, default=datetime.datetime.now, nullable=False)


