from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

class OrderCreate(BaseModel):
    product_id: int
    quantity: int 

class OrderResponse(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    created_at: datetime

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