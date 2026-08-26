from pydantic import BaseModel, Field,EmailStr
from typing import Optional
from datetime import datetime

# ========== Request Schemas ==========

class UserRegister(BaseModel):
    email:str
    password:str=Field(..., min_length=8)
    full_name:str= Field(...,min_length=2,max_length=50)

class UserLogin(BaseModel):
    email:EmailStr
    password:str

# ========== Response Schemas ==========

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    username: Optional[str] = None
    is_active: bool
    is_verified: bool
    role: str
    preferred_language: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse