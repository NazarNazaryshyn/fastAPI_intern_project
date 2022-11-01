from pydantic import BaseModel
from typing import Optional


class CompanyScheme(BaseModel):
    id: Optional[int]
    title: str
    description: str
    is_visible: Optional[bool]
    owner_id: int
    employees: Optional[list]

    class Config:
        orm_mode = True


class InviteScheme(BaseModel):
    id: int
    user_id: int
    company_id: int
    is_accepted: bool

    class Config:
        orm_mode = True