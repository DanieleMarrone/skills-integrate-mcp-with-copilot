"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"


# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserRegister(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: RoleEnum
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


# Club schemas
class ClubBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    max_participants: Optional[int] = None


class ClubCreate(ClubBase):
    pass


class ClubResponse(ClubBase):
    id: int

    class Config:
        from_attributes = True


# Membership schemas
class MembershipBase(BaseModel):
    user_id: int
    club_id: int


class MembershipCreate(MembershipBase):
    pass


class MembershipResponse(MembershipBase):
    id: int
    status: str

    class Config:
        from_attributes = True


class MembershipUpdate(BaseModel):
    status: str = Field(..., regex="^(pending|approved|rejected)$")
