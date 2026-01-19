from .conftest import create_user, get_token
from database_models import Product

def test_user_cannot_create_product(client, db):
    create_user(db, "akash", "akash@gmail.com", "123", "user")
    access_token = get_token(client, "akash@gmail.com", "123")

    response = client.post(
        "/products",
        json = {"name": "a", "description": "a", "price": 1, "quantity": 1, "owner_id": 1},
        headers = {"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 403

def test_owner_can_create_products(client, db):
    create_user(db, "akash", "akash@gmail.com", "123", "owner")
    access_token = get_token(client, "akash@gmail.com", "123")

    response = client.post(
        "/products",
        json = {"name": "a", "description": "a", "price": 1, "quantity": 1, "owner_id": 1},
        headers = {"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 201

def test_owner_can_update_own_products(client, db):
    user = create_user(db, "akash", "akash@gmail.com", "123", "owner")
    access_token = get_token(client, "akash@gmail.com", "123")

    response_create = client.post(
        "/products",
        json = {"name": "a", "description": "a", "price": 1, "quantity": 1},
        headers = {"Authorization": f"Bearer {access_token}"}
    )

    assert response_create.status_code == 201

    data = response_create.json()
    own_product = db.get(Product, data["id"])
    assert own_product.owner_id == user.id

    response_update = client.put(
        f"/products/{data["id"]}",
        json = {"name": "x", "description": "x", "price": 5, "quantity": 5},
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    
    assert response_update.status_code == 200

def test_owner_can_delete_own_products(client, db):
    create_user(db, "akash", "akash@gmail.com", "123", "owner")
    access_token = get_token(client, "akash@gmail.com", "123")

    response_create = client.post(
        "/products",
        json = {"name": "a", "description": "a", "price": 1, "quantity": 1},
        headers = {"Authorization": f"Bearer {access_token}"}
    )
    assert response_create.status_code == 201 
    
    own_product = response_create.json()
    response_delete = client.delete(
        f"/products/{own_product["id"]}",
        headers = {"Authorization": f"Bearer {access_token}"}
    )

    assert response_delete.status_code == 200


def test_owner_cannot_update_others_products(client, db):
    create_user(db, "akash", "akash@gmail.com", "123", "owner") # Owner of product
    create_user(db, "trevor", "trevor@gmail.com", "123", "owner")

    access_token_user1 = get_token(client, "akash@gmail.com", "123")
    response_create = client.post(
        "/products",
        json = {"name": "a", "description": "a", "price": 1, "quantity": 1},
        headers = {"Authorization": f"Bearer {access_token_user1}"}
    )
    assert response_create.status_code == 201

    data = response_create.json()
    
    access_token_user2 = get_token(client, "trevor@gmail.com", "123")
    response_update = client.put(
        f"/products/{data["id"]}",
        json = {"name": "x", "description": "x", "price": 5, "quantity": 5},
        headers = {"Authorization": f"Bearer {access_token_user2}"}
    )

    assert response_update.status_code == 403

def test_owner_cannot_delete_others_products(client, db):
    create_user(db, "akash", "akash@gmail.com", "123", "owner") # Owner of product
    create_user(db, "trevor", "trevor@gmail.com", "123", "owner")

    access_token_user1 = get_token(client, "akash@gmail.com", "123")
    response_create = client.post(
        "/products",
        json = {"name": "a", "description": "a", "price": 1, "quantity": 1},
        headers = {"Authorization": f"Bearer {access_token_user1}"}
    )
    assert response_create.status_code == 201

    product = response_create.json()
    
    access_token_user2 = get_token(client, "trevor@gmail.com", "123")
    response_delete = client.delete(
        f"/products/{product["id"]}",
        headers = {"Authorization": f"Bearer {access_token_user2}"}
    )

    assert response_delete.status_code == 403