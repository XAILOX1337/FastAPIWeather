from sqlalchemy import select
from fastapi import FastAPI
from .database import engine, Base, create_tables, get_db
from .crud import save_currency_rate, create_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends
from .services.weather import get_weather
from .services.currencies import *
from sqlalchemy.ext.asyncio import AsyncEngine
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import redis
from fastapi_cache.backends.redis import RedisBackend

from fastapi_cache.decorator import cache, FastAPICache
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from .services.auth import *



@asynccontextmanager
async def lifespan(app: FastAPI):
    Redis = redis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(Redis), prefix="fastapi-cache")
    await create_tables()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


@app.post("/create_user")
async def CreateUser(username: str, email: str, password: str, db: AsyncSession = Depends(get_db)):
    hashed_password = get_password_hash(password)
    result = await create_user(db = db, username = username, email = email, hashed_password = hashed_password)
    return result


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
    
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]



@app.get("/weather/{city}")
@cache(expire=600)
async def weather(city: str):
    return await get_weather(city)


@app.get("/currencies/{currency}")
@cache(expire=600)
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


