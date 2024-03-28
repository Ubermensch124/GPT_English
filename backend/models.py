from database import Base
from sqlalchemy import JSON, VARCHAR, Column


class WebUser(Base):
	__tablename__ = 'web_user'
	__table_args__ = {'extend_existing': True}

	chat_id = Column(VARCHAR, primary_key=True)
	chat_history = Column(JSON)


class TelegramUser(Base):
	__tablename__ = 'telegram_user'
	__table_args__ = {'extend_existing': True}

	chat_id = Column(VARCHAR, primary_key=True)
	chat_history = Column(JSON)
