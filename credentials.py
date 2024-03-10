import os


if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DIALECT=os.getenv('DIALECT')
DRIVER=os.getenv('DRIVER')
POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_DB=os.getenv('POSTGRES_DB')
POSTGRES_HOST=os.getenv('POSTGRES_HOST')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
