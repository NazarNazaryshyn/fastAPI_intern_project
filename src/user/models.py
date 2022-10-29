from sqlalchemy.orm import relationship, backref

from src.database import Base
from sqlalchemy import Column, String, Integer, Date
from src.company.models import company_employees, company_admins
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
    companies = relationship("Company", backref=backref("owner", lazy="joined"))
    employee_in_companies = relationship("Company", secondary=company_employees, back_populates="employees_in_company")
    admin_in_companies = relationship("Company", secondary=company_admins, back_populates="admins_in_company")

