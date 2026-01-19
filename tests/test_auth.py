from .conftest import create_user, get_token

def test_login_success(client, db):
    create_user(db, "trevor", "trevor@gmail.com", "123", "user")

    response = client.post(
        "/token",
        data = {"username": "trevor@gmail.com", "password": "123"},
        headers = {"Content-Type": "application/x-www-form-urlencoded"},)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure_wrong_password(client, db):
    create_user(db, "akash", "akash@gmail.com", "123", "owner")

    response = client.post(
        "/token",
        data = {"username": "akash@gmail.com", "password": "wrongpass"},
        headers = {"Content-Type": "application/x-www-form-urlencoded"},)
    assert response.status_code == 401

def test_access_without_token(client):
    response = client.get("/products")
    assert response.status_code == 401

def test_access_with_valid_token(client, db):
    create_user(db, "akash", "akash@gmail.com", "123", "owner")
    access_token = get_token(client, "akash@gmail.com", "123")

    response = client.get(
        "/products",
        headers = {"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200

def test_access_with_invalid_token(client):
    response = client.get(
        "/products",
        headers = {"Authorization": "Bearer invalidToken001"})

    assert response.status_code == 401
