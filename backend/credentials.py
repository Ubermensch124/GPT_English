import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YAPGT_API_KEY = os.getenv('YAPGT_API_KEY')
YANDEX_CATALOG_ID = os.getenv('YANDEX_CATALOG_ID')

DIALECT = os.getenv('DIALECT', 'postgresql')
DRIVER = os.getenv('DRIVER', 'psycopg2')

GPT_MODEL: str = os.getenv('GPT_MODEL', 'orca-mini-3b-gguf2-q4_0.gguf')

PRODUCTION = os.getenv('PRODUCTION', 'False')

if PRODUCTION == 'True':
	POSTGRES_USER = os.getenv('POSTGRES_USER_PRODUCTION', 'postgres')
	POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD_PRODUCTION', 'password')
	POSTGRES_HOST = os.getenv('POSTGRES_HOST_PRODUCTION', 'postgres')
	POSTGRES_PORT = os.getenv('POSTGRES_PORT_PRODUCTION', '5432')
	POSTGRES_DB = os.getenv('POSTGRES_DB_PRODUCTION', 'db')

	FASTAPI_API_HOST = os.getenv('FASTAPI_API_HOST_PRODUCTION')
	FASTAPI_API_PORT = os.getenv('FASTAPI_API_PORT_PRODUCTION')
else:
	POSTGRES_USER = os.getenv('POSTGRES_USER_DEVELOPMENT', 'postgres')
	POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD_DEVELOPMENT', 'password')
	POSTGRES_HOST = os.getenv('POSTGRES_HOST_DEVELOPMENT', 'localhost')
	POSTGRES_PORT = os.getenv('POSTGRES_PORT_DEVELOPMENT', '5432')
	POSTGRES_DB = os.getenv('POSTGRES_DB_DEVELOPMENT', 'gpteacher')

	FASTAPI_API_HOST = os.getenv('FASTAPI_API_HOST_DEVELOPMENT')
	FASTAPI_API_PORT = os.getenv('FASTAPI_API_PORT_DEVELOPMENT')


SYSTEM_PROMPT = '### System:\nYou are an AI assistant that knows English extremely well. When user send you message you need to show him his grammatical mistakes.\n\n'
# SYSTEM_PROMPT = "### System:\nТы учитель по русскому языку. Когда пользователь присылает тебе сообщение, твоя задача состоит в том, чтобы указать ему грамматические ошибки в его сообщении. \nСхема ответа: 'Сообщение пользователя -> сообщение пользователя с исправленной грамматикой и пунктуацией | Объяснение грамматических исправлений'. Например, на сообщение 'Привет ты не знать какое сейчас время?' должен быть получен ответ вроде 'Привет ты не знать какое сейчас время? -> Привет, ты не знаешь какое сейчас время? | ...', на месте многоточия должно стоять объяснение в каких местах в предложение пользователь ошибся.\n\n",
PROMPT_TEMPLATE = '### User:\n{0}\n\n### Response:\n'

SYSTEM_TEMPLATE = {
	'Русский язык': {
		'Русский язык': "Ты учитель по русскому языку. Когда пользователь присылает тебе сообщение, твоя задача состоит в том, чтобы указать ему грамматические ошибки в его сообщении. \nСхема ответа: 'Сообщение пользователя -> сообщение пользователя с исправленной грамматикой и пунктуацией | Объяснение грамматических исправлений'. Например, на сообщение 'Привет ты не знать какое сейчас время?' должен быть получен ответ вроде 'Привет ты не знать какое сейчас время? -> Привет, ты не знаешь какое сейчас время? | ...', на месте многоточия должно стоять объяснение в каких местах в предложение пользователь ошибся.",
		'English': "Ты учитель по английскому языку. Когда пользователь присылает тебе сообщение, твоя задача состоит в том, чтобы указать ему грамматические ошибки в его сообщении. \nСхема ответа: 'Сообщение пользователя -> сообщение пользователя с исправленной грамматикой и пунктуацией | Объяснение грамматических исправлений'. Если исправления не нужны, просто напиши пользователю, что всё хорошо.",
	}
}
