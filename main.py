from fastapi import FastAPI
from models import Product

app = FastAPI()

@app.get("/")
def hello():
    return "Welcome to the store"

products = [
    Product(id=1, name="phone", desc="budget phone", price=15000, quantity=25),
    Product(id=2, name="phone", desc="mid range phone", price=25000, quantity=20)
]

@app.get("/products")
def show():
    return products

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
        

