from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

class Currencies(Base):
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True)
    currency = Column(String, unique=False)
    rate = Column(Float)
    date = Column(DateTime, default=datetime.now)