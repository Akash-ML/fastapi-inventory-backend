from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

url = "postgresql://postgres:2005@localhost:5432/fastapi-app"

engine = create_engine(url)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
