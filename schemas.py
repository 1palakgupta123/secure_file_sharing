from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    role: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
