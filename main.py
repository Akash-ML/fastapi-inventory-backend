from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, UTC

from database_models import Base, Product, User
from database import engine, get_db
import auth
from models import ProductCreate, ProductResponse, UserCreate, UserResponse, Token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def hello():
    return {"message": "Welcome to the Inventory Tracker"}

@app.get("/products", response_model=list[ProductResponse])
def get_all_products(user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    all_products = db.query(Product).order_by(Product.id).all()

    return all_products

@app.get("/products/{id}", response_model=ProductResponse)
def get_product_by_id(id: int, user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    db_product = db.get(Product, id)
    
    if db_product is None:
        raise HTTPException (
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Product not found"
        )

    return db_product
    

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_product(product: ProductCreate, user: User = Depends(auth.require_role("owner")), db: Session = Depends(get_db)):
    new_product = Product (
        name = product.name,
        description = product.description,
        price = product.price,
        quantity = product.quantity,
        owner_id = user.id
    ) 
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@app.put("/products/{id}", response_model=ProductResponse)
def update_product(id: int, product: ProductCreate, user: User = Depends(auth.require_role("owner")), db: Session = Depends(get_db)):
    db_product = db.get(Product, id)
    
    if db_product is None:
        raise HTTPException (
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Product not found"
        )

    if db_product.owner_id != user.id:
        raise HTTPException (
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not enough permissions"
        )

    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.quantity = product.quantity
    db_product.updated_at = datetime.now(tz=UTC)
    
    db.commit()
    db.refresh(db_product)
    return db_product
        

@app.delete("/products/{id}")
def delete_product(id: int, user: User = Depends(auth.require_role("owner")), db: Session = Depends(get_db)):

    db_product = db.get(Product, id)

    if db_product is None:
        raise HTTPException (
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Product not found"
        )

    if db_product.owner_id != user.id:
        raise HTTPException (
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not enough permissions"
        )
    
    db.delete(db_product)
    db.commit()
    
    return {"message": "Product deleted"}

# Endpoints for user authenication

@app.post("/register", response_model = UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    old_user = db.query(User).filter(user_data.email == User.email).first()
    if old_user:
        raise HTTPException (
            status_code = 401,
            detail = "User already exists"
        )
    
    user_data.role = user_data.role.lower()
    if user_data.role not in ["user", "owner"]:
        user_data.role = "user"

    hashed_pass = auth.create_hash(user_data.password)

    db_user = User (
        name = user_data.name,
        email = user_data.email,
        role = user_data.role,
        hashed_pwd = hashed_pass,
        is_active = True
    )
    db.add(db_user)
    db.commit()

    return db_user

@app.post("/token", response_model = Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not auth.verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException (
            status_code = 401,
            detail = "Incorrect username or password"
        )
    
    access_token = auth.create_access_token({"sub": user.email, "role": user.role}, timedelta(minutes=auth.TOKEN_EXPIRE_MINUTES))

    return {"access_token": access_token, "token_type": "bearer"}
