from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    balance: Optional[Decimal] = Field(default=Decimal("10000.00000000"), ge=0)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    name: str
    email: str
    balance: Decimal

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None
