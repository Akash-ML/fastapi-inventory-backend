from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from datetime import datetime, UTC

Base = declarative_base()

class Product(Base):

    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(tz=UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(tz=UTC), nullable=False)

    owner = relationship("User", back_populates="products")
    
    __table_args__ = (
        Index("idx_product_name", name),
        Index("idx_owner_id", owner_id)
    )

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False)
    hashed_pwd = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)

    products = relationship("Product", back_populates="owner")