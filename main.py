import os
import logging
import json

from pydub import AudioSegment
from telegram import Update
from telegram.ext import (
    filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
)

from credentials import TELEGRAM_BOT_TOKEN
from make_audio import get_speech_from_gtts
from text_generator import get_random_text
from whisper_test import extract_text_from_audio
from database import Base, engine, Session
from models import MyObject
from gpt4all_test import get_response

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


async def get_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Бот отсылает рандомный отрывок из 'Дюны' в виде голосового сообщения """
    filepath = get_speech_from_gtts(get_random_text())
    with open(filepath, 'rb') as voice_file:
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_file)
    os.remove(filepath)


async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Бот принимает от нас голосовое сообщение """
    session = Session()
    res = session.query(MyObject).filter(MyObject.chat_id == update.effective_chat.id).first()
    chat_history = None
    if res is not None:
        chat_history = json.loads(res.chat_history)
    
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    user = update.effective_user.username
    filename_ogg = f"user_audio/{user}.ogg"
    filename_mp3 = f"user_audio/{user}.mp3"
    
    await voice_file.download_to_drive(filename_ogg)
    
    ogg_audio = AudioSegment.from_file(filename_ogg, format="ogg")
    _ = ogg_audio.export(filename_mp3, format="mp3")
    
    user_text = extract_text_from_audio(path=filename_mp3)
    model_answer = get_response(current_prompt=user_text, chat_history=chat_history)
    
    serialize_history = json.dumps(model_answer['chat_history'])
    to_delete = session.query(MyObject).filter(MyObject.chat_id == update.effective_chat.id).first()
    if to_delete:
        session.delete(to_delete)
    new_obj = MyObject(chat_id=update.effective_chat.id, chat_history=serialize_history)
    session.add(new_obj)
    session.commit()
    session.close()
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Вот твой текст: {user_text}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=model_answer['response'])
    
    filepath = get_speech_from_gtts(model_answer['response'])
    with open(filepath, 'rb') as voice_file:
        await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_file)
    os.remove(filepath)
    # os.remove(filename_ogg)
    # os.remove(filename_mp3)


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
    get_voice_handler =  CommandHandler('get_voice', get_voice)
    voice_handler = MessageHandler(filters.VOICE, voice)
    delete_context_handler = CommandHandler('delete_context', delete_context)
    help_handler = CommandHandler('help', help_bot)

    application.add_handler(start_handler)
    application.add_handler(get_voice_handler)
    application.add_handler(voice_handler)
    application.add_handler(delete_context_handler)
    application.add_handler(help_handler)

    application.run_polling()
