from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


# ... means required field
class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(None, max_length=500)


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(None, max_length=500)


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True
