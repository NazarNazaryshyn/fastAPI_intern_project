from sqlalchemy.orm import relationship

from src.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Table, Boolean


company_employees = Table(
    "company_employees", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("company_id", Integer, ForeignKey("companies.id"))
)


company_admins = Table(
    "company_admins", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("company_id", Integer, ForeignKey("companies.id"))
)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_visible = Column(Boolean, nullable=False, default=True)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    employees_in_company = relationship("User", secondary=company_employees, back_populates="employee_in_companies")
    admins_in_company = relationship("User", secondary=company_admins, back_populates="admin_in_companies")


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    company_id = Column(Integer, ForeignKey("companies.id", ondelete='CASCADE'))
    is_accepted = Column(Boolean)


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    company_id = Column(Integer, ForeignKey("companies.id", ondelete='CASCADE'))
    is_accepted = Column(Boolean)


