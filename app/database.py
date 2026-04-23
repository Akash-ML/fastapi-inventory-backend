from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

DB_URL = settings.database_url

engine = create_engine(DB_URL)

session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = session_maker()

    try:
        yield db
    finally:
        db.close()