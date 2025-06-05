from sqlalchemy.orm import Session
from . import models
from datetime import datetime
from databases import Database
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Currencies
import httpx
from datetime import date

async def create_currency_rate(currency_code: str, rate: float):
    query = Currencies.insert().values(
        currency_code=currency_code,
        rate=rate
    )
    await Database.execute(query)

async def save_currency_rate(db: AsyncSession, currency: str, rate: float, date: date):
    db_obj = Currencies(currency=currency, rate=rate, date=date)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj