from typing import Optional
from pydantic import BaseModel, EmailStr
import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: str
    is_active: bool
    influence_score: Optional[int] = 0
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Additional properties to return via API
class UserResponse(UserInDBBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
