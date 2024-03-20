from sqlalchemy import Column, JSON, VARCHAR

from database import Base


class WebUser(Base):
    __tablename__ = 'web_user'
    __table_args__ = {'extend_existing':True}

    chat_id = Column(VARCHAR, primary_key=True)
    chat_history = Column(JSON)
