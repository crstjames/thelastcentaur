from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: Optional[str] = None
    exp: Optional[int] = None

class UserCreate(BaseModel):
    """User creation schema."""
    username: str
    email: EmailStr
    password: str
    
    @field_validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str

class UserResponse(BaseModel):
    """User response schema."""
    id: str
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) 