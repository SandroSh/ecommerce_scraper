from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecommerce_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
