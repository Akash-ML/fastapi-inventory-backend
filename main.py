from fastapi import FastAPI
from models import Product

import database_models
from database import session, engine


app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)


products = [
    Product(id=1, name="phone", description="budget phone", price=15000, quantity=25),
    Product(id=2, name="phone", description="mid range phone", price=25000, quantity=20),
    Product(id=3, name="phone", description="premium phone", price=45000, quantity=10),
    Product(id=4, name="tablet", description="budget tablet", price=18000, quantity=15),
    Product(id=5, name="laptop", description="gaming laptop", price=75000, quantity=5)
]

def init_db():
    db = session()

    count = db.query(database_models.Product).count

    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))

        db.commit()

init_db()


@app.get("/")
def hello():
    return "Welcome to the store"


@app.get("/products")
def get_all_products():
    db = session()
    
    return db.query(database_models.Product).all()

@app.get("/products/{id}")
def get_product_by_id(id: int):
    for product in products:
        if product.id == id:
            return product
    
    return "Product not found"


@app.post("/products")
def add_product(product: Product):
    products.append(product)

    return "Product Added"


@app.put("/products")
def update_product(id: int, product: Product):
    for i in range(len(products)):
        if products[i].id == id:
            products[i] = product

            return "Product Updated"


@app.delete("/products")
def delete_product(id: int):
    for i in range(len(products)):
        if products[i].id == id:
            del products[i]
            
            return "Product deleted"
        

