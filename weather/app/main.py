from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi import FastAPI, Depends
from .services.weather import get_weather
from .services.currencies import fetch_currency_rates

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}



@app.get("/weather/{city}")
async def weather(city: str):
    return await get_weather(city)

@app.get("/currencies/{currency}")
async def currency_rates(currency):
    return fetch_currency_rates(currency)