from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserLogin, UserRegister, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from app.models.user import User


router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register",response_model=TokenResponse,status_code=status.HTTP_201_CREATED)
def register(user_data:UserRegister,db:Session=Depends(get_db)):
    """
    Register a new user.
    """
    user=AuthService.register_user(db,user_data)
    #Automatically log user in After registration

    login_result=AuthService.login_user(db,UserLogin(email=user.email,password=user_data.password))
    return login_result

@router.post("/login",response_model=TokenResponse,status_code=status.HTTP_200_OK)
def login(user_data:UserLogin,db:Session=Depends(get_db)):
    """
    Login a user.
    """
    login_result=AuthService.login_user(db,user_data)
    return login_result

@router.get("/me",response_model=UserResponse,status_code=status.HTTP_200_OK)
def read_user(current_user:User=Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user 

