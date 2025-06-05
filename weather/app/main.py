from sqlalchemy import select
from fastapi import FastAPI
from .database import engine, Base, create_tables, get_db
from .crud import save_currency_rate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends
from .services.weather import get_weather
from .services.currencies import *
from sqlalchemy.ext.asyncio import AsyncEngine
from contextlib import asynccontextmanager




"""
Handles the startup and shutdown events of the FastAPI application.

This asynchronous context manager is used to perform setup actions when the application starts and cleanup actions when it shuts down.
On startup, it creates the database tables using SQLAlchemy metadata.

Args:
    app (FastAPI): The FastAPI application instance.

Yields:
    None: This context manager does not yield any value, but allows for code execution before and after the application lifecycle.
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await create_tables()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather/{city}")
async def weather(city: str):
    return await get_weather(city)


@app.get("/currencies/{currency}")
async def currency_rates(currency):
    return await fetch_currency_rates(currency)


@app.get("/save_currency_rate/{currency}")
async def get_and_save_currency_rate(currency: str, db: AsyncSession = Depends(get_db)):
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        rate = data["Valute"][currency]["Value"]
    result = await save_currency_rate(db, currency, rate, datetime.now().date())
    return result


@app.get("/get_all_rates", response_model=None)  
async def get_all_rates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Currencies))
    records = result.scalars().all()
    return [{"id": r.id, "currency": r.currency, "rate": r.rate} for r in records]


