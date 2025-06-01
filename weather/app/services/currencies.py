import requests
from celery import Celery

def fetch_currency_rates(currency: str):
    url = f"https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url).json()
    currency_rate = response["Valute"][currency]
    return currency_rate




celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
def update_currency_rates():
    rates = fetch_currency_rates()
    