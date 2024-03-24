import os

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YAPGT_API_KEY = os.getenv('YAPGT_API_KEY')
YANDEX_CATALOG_ID = os.getenv('YANDEX_CATALOG_ID')

DIALECT=os.getenv('DIALECT')
DRIVER=os.getenv('DRIVER')
POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_DB=os.getenv('POSTGRES_DB')
POSTGRES_HOST=os.getenv('POSTGRES_HOST')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
