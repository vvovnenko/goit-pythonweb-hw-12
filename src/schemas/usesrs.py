from pydantic import BaseModel, ConfigDict

from src.database.models import UserRole


class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole
