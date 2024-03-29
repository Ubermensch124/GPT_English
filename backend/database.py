from credentials import (
	DIALECT,
	DRIVER,
	POSTGRES_DB,
	POSTGRES_HOST,
	POSTGRES_PASSWORD,
	POSTGRES_PORT,
	POSTGRES_USER,
)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists

engine = create_engine(
	f'{DIALECT}+{DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
)

print(engine.url)

def check_db(engine):
	if not database_exists(engine.url):
		create_database(engine.url)

Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()
