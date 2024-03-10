from sqlalchemy import Column, Integer, JSON

from database import Base


class MyObject(Base):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing':True}

    chat_id = Column(Integer, primary_key=True)
    chat_history = Column(JSON)
