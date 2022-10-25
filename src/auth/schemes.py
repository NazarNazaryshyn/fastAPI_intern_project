from pydantic import BaseModel


class TokenScheme(BaseModel):
    token: str

    class Config:
        orm_mode = True