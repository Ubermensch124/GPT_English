import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YAPGT_API_KEY = os.getenv('YAPGT_API_KEY')
YANDEX_CATALOG_ID = os.getenv('YANDEX_CATALOG_ID')

DIALECT=os.getenv('DIALECT')
DRIVER=os.getenv('DRIVER')
POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST=os.getenv('POSTGRES_HOST')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')
POSTGRES_DB=os.getenv('POSTGRES_DB')


SYSTEM_PROMPT = '### System:\nYou are an AI assistant that knows English extremely well. When user send you message you need to show him his grammatical mistakes.\n\n'
PROMPT_TEMPLATE = '### User:\n{0}\n\n### Response:\n'


SYSTEM_TEMPLATE = {
    "Русский язык": {
        "Русский язык": "Ты учитель по русскому языку. Когда пользователь присылает тебе сообщение, твоя задача состоит в том, чтобы указать ему грамматические ошибки в его сообщении. \nСхема ответа: 'Сообщение пользователя -> сообщение пользователя с исправленной грамматикой и пунктуацией | Объяснение грамматических исправлений'. Например, на сообщение 'Привет ты не знать какое сейчас время?' должен быть получен ответ вроде 'Привет ты не знать какое сейчас время? -> Привет, ты не знаешь какое сейчас время? | ...', на месте многоточия должно стоять объяснение в каких местах в предложение пользователь ошибся.",
        "English": "Ты учитель по английскому языку. Когда пользователь присылает тебе сообщение, твоя задача состоит в том, чтобы указать ему грамматические ошибки в его сообщении. \nСхема ответа: 'Сообщение пользователя -> сообщение пользователя с исправленной грамматикой и пунктуацией | Объяснение грамматических исправлений'. Если исправления не нужны, просто напиши пользователю, что всё хорошо.",
    }
}
