from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(String)
    brand = Column(String)
    category = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product(name='{self.name}', brand='{self.brand}', category='{self.category}')>"
