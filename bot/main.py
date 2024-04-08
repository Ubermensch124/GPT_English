import logging
import uuid

import requests
from credentials import FASTAPI_API_HOST, FASTAPI_API_PORT, INSTRUCTION, TELEGRAM_BOT_TOKEN
from pydub import AudioSegment
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

FASTAPI_API = f"http://{FASTAPI_API_HOST}:{FASTAPI_API_PORT}"


async def get_user_text_from_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
	voice_file = await context.bot.get_file(update.message.voice.file_id)
	user = update.effective_user.username
	ogg_path = f'../shared/{user}.ogg'
	mp3_path = f'../shared/{user}.mp3'

	await voice_file.download_to_drive(ogg_path)

	ogg_audio = AudioSegment.from_file(ogg_path, format='ogg')
	_ = ogg_audio.export(mp3_path, format='mp3')

	with open(mp3_path, 'rb') as file:
		response = requests.post(
			FASTAPI_API + '/audio_prompt_to_text',
			files={'audio': file},
		)
		user_text = response.json()['text']
		return user_text


def get_gpt_text_response(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> str:
	chat_id = update.effective_chat.id
	url = FASTAPI_API + '/text_prompt'
	headers = {'userId': str(chat_id), 'isTelegram': 'True'}
	response = requests.post(url=url, headers=headers, json={'text': user_text}, stream=True)

	gpt_answer = ''
	for chunk in response.iter_content(decode_unicode=True):
		gpt_answer += chunk
	return gpt_answer


def get_gpt_audio_response(gpt_text: str):
	url = FASTAPI_API + '/get_audio'
	response = requests.post(url=url, json={'text': gpt_text})
	path = "../shared/" + str(uuid.uuid4()) + ".mp3"
	with open(path, "wb") as audio_file:
		audio_file.write(response.content)
 
	return path


async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Бот принимает от нас голосовое сообщение"""
	user_text = await get_user_text_from_audio(update, context)
	gpt_response = get_gpt_text_response(update, context, user_text)
	await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Вот твой текст: {user_text}')
	await context.bot.send_message(chat_id=update.effective_chat.id, text=gpt_response)
	gpt_audio = get_gpt_audio_response(gpt_text=gpt_response)
		
	with open(gpt_audio, 'rb') as voice_file:
		await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_file)


async def delete_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Удаление контекста диалога"""
	chat_id = update.effective_chat.id
	headers = {'userId': str(chat_id), 'isTelegram': 'True'}
	url = FASTAPI_API + '/reset_conversation'
	_ = requests.delete(url=url, headers=headers)
	await context.bot.send_message(chat_id=update.effective_chat.id, text='Контекст удалён')


async def help_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Инструкция по работе с ботом"""
	await context.bot.send_message(chat_id=update.effective_chat.id, text=INSTRUCTION)


if __name__ == '__main__':
	application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

	voice_handler = MessageHandler(filters.VOICE, voice)
	delete_context_handler = CommandHandler('delete_context', delete_context)
	help_handler = CommandHandler('help', help_bot)

	application.add_handler(voice_handler)
	application.add_handler(delete_context_handler)
	application.add_handler(help_handler)

	application.run_polling()
