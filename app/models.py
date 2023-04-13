from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    admin = "admin"
    mortal = "simple mortal"
    dev = "dev"


class UserSchema(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    role: RoleEnum
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime


class CreateUserSchema(UserSchema):
    hashed_pass: str


class UpdateUserSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[RoleEnum]


class LoginUserSchema(BaseModel):
    username: EmailStr
    password: str


class JWTResponseSchema(BaseModel):
    access_token: str
    refresh_token: str


class JWTTokenSchema(BaseModel):
    exp: int
    sub: str
