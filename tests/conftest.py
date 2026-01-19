from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database_models import Base, User
from main import app
from database import get_db
from auth import create_hash

import pytest, httpx

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db):
    def get_test_db():
        yield db

    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def create_user(db, name, email, password, role):
    hashed_pass = create_hash(password)

    db_user = User (
        name = name,
        email = email,
        role = role,
        hashed_pwd = hashed_pass,
        is_active = True
    )
    db.add(db_user)
    db.commit()

    return db_user

def get_token(client, email, password):
    response = client.post(
        "/token",
        data = {"username": email, "password": password},
        headers = {"Content-Type": "application/x-www-form-urlencoded"})
    
    token = response.json()["access_token"]
    return token