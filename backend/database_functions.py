import json

from models import TelegramUser, WebUser


def from_where_user(session, userId, isTelegram):
	user = None
	if isTelegram == "True":
		user = session.query(TelegramUser).filter(TelegramUser.chat_id == userId).first()
	else:
		user = session.query(WebUser).filter(WebUser.chat_id == userId).first()
	return user


def get_chat_history(session, userId, isTelegram):
	"""Return chat history for user with userId"""
	user = from_where_user(session, userId, isTelegram)
	chat_history = None
	if user is not None:
		chat_history = json.loads(user.chat_history)

	return chat_history


def delete_user(session, userId, isTelegram) -> None:
	"""Delete user DB raw with userId"""
	user_to_delete = from_where_user(session, userId, isTelegram)
	if user_to_delete:
		session.delete(user_to_delete)
		session.commit()


def save_chat_history(session, chat_history, userId, isTelegram):
	"""Save chat history for user with userId"""
	delete_user(session, userId, isTelegram)
	serialize_history = json.dumps(chat_history)
	if isTelegram == "True":
		new_obj = TelegramUser(chat_id=userId, chat_history=serialize_history)
	else:
		new_obj = WebUser(chat_id=userId, chat_history=serialize_history)
	session.add(new_obj)
	session.commit()
