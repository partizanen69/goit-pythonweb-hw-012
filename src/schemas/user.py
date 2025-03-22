from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# ... is means required
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr # TODO: to check if this field is required
    password: str = Field(..., min_length=6, max_length=50)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr # TODO: to check if this field is required
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer" 
