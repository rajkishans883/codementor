from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister
from app.utils.Security import hash_password, verify_password, create_access_token, verify_token
from datetime import datetime, timedelta
from app.config import settings
import jwt
import bcrypt

class AuthService:

    @staticmethod
    def register_user(db:Session, user_data:UserRegister)->User:

        #check if emial already exists
        exiting_user = db.query(User).filter(User.email == user_data.email).first()
        if exiting_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        #Create new user
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hash_password(user_data.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def login_user(db:Session, login_data:UserLogin)->dict:
        user=db.query(User).filter(User.email==login_data.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        #verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

        #create access token
        access_token=create_access_token(
            data={"sub":str(user.id),"email":user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user