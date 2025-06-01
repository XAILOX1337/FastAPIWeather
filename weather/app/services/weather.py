import os
import requests
import redis
from dotenv import load_dotenv
import json


load_dotenv()



async def get_weather(city: str) -> dict:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    
    return response.json()