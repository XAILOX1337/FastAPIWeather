from sqlalchemy import Column, Integer, String, Float, Date, Sequence
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

"""
A class representing the `currencies` table in the database.

This class maps to the `currencies` table and defines the structure of its records,
including fields such as currency name, exchange rate, and the date of the record.

Attributes:
    id (int): The primary key of the record.
    currency (str): The name of the currency.
    rate (float): The exchange rate of the currency.
    date (datetime): The timestamp when the record was created, defaults to the current time.
"""
class Currencies(Base):
    __tablename__ = "currencies"
    id = Column(Integer, Sequence('currencies_id_seq'), primary_key=True)
    currency = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    date = Column(Date, default=datetime.now().date(), nullable=False)