from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class ContactModel(BaseModel):
    firstname: str = Field(min_length=2, max_length=50)
    lastname: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(min_length=5, max_length=150)
    phone: str = Field(min_length=7, max_length=30)
    birthday: date
    comment: Optional[str] = Field(None, min_length=1, max_length=500)


class ContactResponseModel(ContactModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] | None
    model_config = ConfigDict(from_attributes=True)
