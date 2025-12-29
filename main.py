from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from models import Product, UserCreate, UserResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

import database_models
from database import session_maker, engine, get_db
import auth
import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

database_models.Base.metadata.create_all(bind=engine)

products = [
    Product(id=1, name="phone", description="budget phone", price=15000, quantity=25),
    Product(id=2, name="phone", description="mid range phone", price=25000, quantity=20),
    Product(id=3, name="phone", description="premium phone", price=45000, quantity=10),
    Product(id=4, name="tablet", description="budget tablet", price=18000, quantity=15),
    Product(id=5, name="laptop", description="gaming laptop", price=75000, quantity=5)
]

def init_db():
    db = session_maker()

    count = db.query(database_models.Product).count

    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))

        db.commit()

    db.close()

init_db()

@app.get("/")
def hello():
    return "Welcome to the store"

@app.get("/products")
def get_all_products(user: database_models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    all_products = db.query(database_models.Product).all()

    return all_products

@app.get("/products/{id}")
def get_product_by_id(id: int, user: database_models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    
    if db_product:
        return db_product
    else:
        return "Product not found"

@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()

    return "Product Added"

@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    
    if db_product is None:
        return "Id not found"

    # To maintain the original id
    db.query(database_models.Product).filter(database_models.Product.id == id).update(product.model_dump())
    db_product.id = id
    
    db.commit()
    return "Product Updated"
        

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):

    deleted_row_count = db.query(database_models.Product).filter(database_models.Product.id == id).delete()
    db.commit()

    return f"{deleted_row_count} Product deleted"
    

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = database_models.User (
        name = user.name,
        email = user.email,
        role = user.role,
    )

    db.add(db_user)
    db.commit()

    return "User Created"

# Endpoints for user authenication

@app.post("/register", response_model = UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    old_user = db.query(database_models.User).filter(user_data.email == database_models.User.email).first()
    if old_user:
        raise HTTPException (
            status_code = 401,
            detail = "User already exists"
        )
    
    hashed_pass = auth.create_hash(user_data.password)

    db_user = database_models.User (
        name = user_data.name,
        email = user_data.email,
        role = user_data.role,
        hashed_pwd = hashed_pass
    )
    db.add(db_user)
    db.commit()

    return db_user

@app.post("/token", response_model = models.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):    # Depends()
    user = db.query(database_models.User).filter(database_models.User.email == form_data.username).first()

    if not user or not auth.verify_pwd(form_data.password, user.hashed_pwd):
        raise HTTPException (
            status_code = 401,
            detail = "Incorrect username or password"
        )
    
    access_token = auth.create_access_token({"sub": user.email}, timedelta(minutes=auth.TOKEN_EXPIRE_MINUTES))

    return {"access_token": access_token, "token_type": "bearer"}