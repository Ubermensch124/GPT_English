from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from credentials import (
    DIALECT, DRIVER, POSTGRES_USER, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_PASSWORD
)

engine = create_engine(f"{DIALECT}+{DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()
