import os
import logging
import json
import requests
import time

from pydub import AudioSegment
from telegram import Update
from telegram.ext import (
    filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
)

import aiofiles.os

from credentials import TELEGRAM_BOT_TOKEN
from database import Base, engine, Session
from models import MyObject

Base.metadata.create_all(bind=engine)

INSTRUCTION = """Вас приветствует GPT для изучения английского.\n
Вы можете в любой момент начать писать мне сообщения на английском или отправлять голосовые. 
Я буду анализировать ваши сообщения на наличие грамматических ошибок. 
Также на каждое ваше сообщение я буду отвечать как живой человек, чтобы вам было интересно вести беседу.\n
Если вы чувствуете, что тема диалога вас не устраивает, то можете воспользоваться функцией /delete_context или /start."""

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Обнуление бота, запуск снова """
    session = Session()
    to_delete = session.query(MyObject).filter(MyObject.chat_id == update.effective_chat.id).first()
    if to_delete:
        session.delete(to_delete)
        session.commit()
    session.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Для подробной информации используйте \help.")


async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Бот принимает от нас голосовое сообщение """
    session = Session()
    res = session.query(MyObject).filter(MyObject.chat_id == update.effective_chat.id).first()
    chat_history = None
    if res is not None:
        chat_history = json.loads(res.chat_history)

    voice_file = await context.bot.get_file(update.message.voice.file_id)
    user = update.effective_user.username
    ogg_path = f"../shared/{user}.ogg"
    mp3_path = f"../shared/{user}.mp3"

    await voice_file.download_to_drive(ogg_path)

    ogg_audio = AudioSegment.from_file(ogg_path, format="ogg")
    _ = ogg_audio.export(mp3_path, format="mp3")

    response = requests.post(
        "http://localhost:8000/get_response_to_the_audio",
        json={"chat_history": {"chat": chat_history}, "path_to_user_audio": {"path": mp3_path}},
        timeout=45,
    )
    response = response.json()
    user_text, model_answer, updated_chat, gpt_audio_path = response.values()

    serialize_history = json.dumps(updated_chat)
    to_delete = session.query(MyObject).filter(MyObject.chat_id == update.effective_chat.id).first()
    if to_delete:
        session.delete(to_delete)
    new_obj = MyObject(chat_id=update.effective_chat.id, chat_history=serialize_history)
    session.add(new_obj)
    session.commit()
    session.close()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вот твой текст: {user_text}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=model_answer)
    with open(gpt_audio_path, 'rb') as voice_file:
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_file)

    os.remove(gpt_audio_path)


async def delete_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Удаление контекста диалога """
    session = Session()
    to_delete = session.query(MyObject).filter(MyObject.chat_id == update.effective_chat.id).first()
    if to_delete:
        session.delete(to_delete)
        session.commit()
    session.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Контекст удалён")


async def help_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Инструкция по работе с ботом """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=INSTRUCTION)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(filters.VOICE, voice)
    delete_context_handler = CommandHandler('delete_context', delete_context)
    help_handler = CommandHandler('help', help_bot)

    application.add_handler(start_handler)
    application.add_handler(voice_handler)
    application.add_handler(delete_context_handler)
    application.add_handler(help_handler)

    application.run_polling()
