from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    phone: str
    email: EmailStr
    role: str
    district: Optional[str] = None
    state: Optional[str] = "Assam"
    language: Optional[str] = "en"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None

class PreferencesUpdate(BaseModel):
    language: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None

class UserResponse(UserBase):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
