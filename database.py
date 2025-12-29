from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

url = "postgresql://postgres:2005@localhost:5432/fastapi-app"

engine = create_engine(url)

session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = session_maker()

    try:
        yield db
    finally:
        db.close