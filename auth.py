from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import timedelta, datetime
import jwt
from models import Token, TokenData
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import get_db
from database_models import User


SECRET_KEY = "aaf318be2283aac0c0ca9fa68594b3ed887ecea1412e0d2a439730653874c140"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Security Functions

def create_hash(pwd: str):
    return password_hash.hash(password=pwd)

def verify_pwd(pwd: str, hashed_pwd: str) -> bool:
    return password_hash.verify(pwd, hashed_pwd)

def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_email: str = payload.get("sub")

        if user_email is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Unable to verify credentials",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        
        return TokenData(email=user_email)
    
    except jwt.PyJWTError:
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Unable to verify credentials",
                headers = {"WWW-Authenticate": "Bearer"}
            )
    
# Functions to get the current active user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = verify_token(token)

    current_user = db.query(User).filter(User.email == token_data.email).first()
    if current_user is None:
        raise HTTPException (
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    return current_user

def get_current_active_user(user: User = Depends(get_current_user)):
    if user.is_active is False:
        raise HTTPException (
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Inactive user"
        )
    
    return user

