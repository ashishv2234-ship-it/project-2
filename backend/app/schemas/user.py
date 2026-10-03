from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    phone: str
    email: EmailStr
    role: str
    district: str | None = None
    state: str | None = "Assam"
    language: str | None = "en"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    district: str | None = None
    state: str | None = None
    language: str | None = None
    status: str | None = None


class PreferencesUpdate(BaseModel):
    language: str | None = None
    district: str | None = None
    state: str | None = None


class UserResponse(UserBase):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
