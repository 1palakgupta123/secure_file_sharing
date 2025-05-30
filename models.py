from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str     # <-- change from hashed_password to password for simplicity
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
