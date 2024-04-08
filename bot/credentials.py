import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
FASTAPI_API_HOST = os.getenv('FASTAPI_API_HOST', "localhost")
FASTAPI_API_PORT = os.getenv('FASTAPI_API_PORT', 8000)

INSTRUCTION = """Вас приветствует GPT для изучения английского.\n
Вы можете в любой момент начать писать мне сообщения на английском или отправлять голосовые. 
Я буду анализировать ваши сообщения на наличие грамматических ошибок. 
Также на каждое ваше сообщение я буду отвечать как живой человек, чтобы вам было интересно вести беседу.\n
Если вы чувствуете, что тема диалога вас не устраивает, то можете воспользоваться функцией /delete_context или /start."""
