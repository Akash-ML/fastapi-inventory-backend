from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from sqlalchemy.orm import Session

import database_models
from database import session, engine


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

def get_db():
    db = session()

    try:
        yield db
    finally:
        db.close

def init_db():
    db = session()

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
def get_all_products(db: Session = Depends(get_db)):
    all_products = db.query(database_models.Product).all()

    return all_products

@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
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
    
