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
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")





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

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

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


