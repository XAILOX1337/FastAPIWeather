import requests
from celery import Celery
from sqlalchemy import create_engine
from ..crud import create_currency_rate
from ..database import SessionLocal
from ..models import Currencies
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

async def fetch_currency_rates(currency: str):
    url = f"https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url).json()
    currency_rate = response["Valute"][currency]
    return currency_rate

async def get_currency_rate(currency: str):
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return data["Valute"][currency]["Value"]












    