from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    youtube_api_key: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    youtube_api_key: Optional[str] = None

    class Config:
        orm_mode = True # Changed from from_attributes = True for Pydantic v1 compatibility

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str # For internal use, not exposed in User schema

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 