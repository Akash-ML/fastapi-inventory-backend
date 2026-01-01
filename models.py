from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
    
class UserCreate(BaseModel):
    name: str
    email: str 
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str 
    email: str
    role: str
    is_active: bool

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str 
    token_type: str 

class TokenData(BaseModel):
    email: Optional[str] = None 