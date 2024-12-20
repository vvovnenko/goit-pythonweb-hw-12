from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    password: str
