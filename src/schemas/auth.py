from pydantic import BaseModel, EmailStr, Field

from src.core.security import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role = Role.trader


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = {"from_attributes": True}

