import logging
import os
import shutil
from contextlib import asynccontextmanager
from enum import Enum
from tempfile import NamedTemporaryFile
from typing import Dict, List, Literal

import uvicorn
from database import Base, Session, engine
from database_functions import delete_user, get_chat_history, save_chat_history
from fastapi import Depends, FastAPI, File, Header, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from gpt4all_test import get_model, get_yagpt
from make_audio import get_speech_from_gpt
from pydantic import BaseModel
from requests import Session as ReqSession
from whisper_audio_extraction import extract_text_from_audio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class LLM(str, Enum):
	GPT4ALL = 'gpt4all'
	YANDEX = 'Yandex GPT-lite'
	GIGACHAT = 'Gigachat-lite'


class Lang(str, Enum):
	ENGLISH = 'English'
	RUSSIAN = 'Русский язык'
	FRENCH = 'French'
	SPANISH = 'Spanish'


class Role(str, Enum):
	SYSTEM = 'system'
	USER = 'user'
	ASSISTANT = 'assistant'


class RoleContent(BaseModel):
	role: Role
	content: str


class ChatHistory(BaseModel):
	chat: List[Dict[Role, RoleContent]] | None = None


class TextPrompt(BaseModel):
	text: str
	voice: Literal['Female', 'Male'] | None = 'Female'
	llm: LLM | None = LLM.GPT4ALL
	native_lang: Lang | None = Lang.RUSSIAN
	foreign_lang: Lang | None = Lang.ENGLISH


paths = ['http://localhost', 'http://127.0.0.1']
ports = [80, 3000, 5173, 4173, 5500]
origins = [f'{path}:{port}' for port in ports for path in paths]
origins.append('http://localhost')

model = get_model()


def get_session():
	"""Open Postgres session"""
	session = Session()
	try:
		yield session
	finally:
		session.close()


def get_req_session():
	"""Open requests session"""
	session = ReqSession()
	try:
		yield session
	finally:
		session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""on_startup alternative"""
	Base.metadata.create_all(bind=engine)
	if os.path.exists('../shared'):
		shutil.rmtree('../shared')
	os.mkdir('../shared')
	yield


app = FastAPI(title='GPTeacher', version='0.1', lifespan=lifespan, log_config=logging.getLogger)

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)


async def stream_gpt4all(model, chat_history, prompt, session, userId, isTelegram):
	"""Stream gpt4all tokens"""
	new_chat = []
	with model.chat_session():
		if chat_history is not None:
			model.current_chat_session = chat_history
		flag = True
		for token in model.generate(prompt=prompt, streaming=True):
			if flag:
				token = token[1:]
				flag = False
			yield token
		new_chat = model.current_chat_session
	save_chat_history(session, new_chat, userId, isTelegram)


async def stream_yagpt(yagpt, chat_history, req_ses, session, userId, isTelegram):
	"""Stream yandex gpt tokens"""
	resp = req_ses.send(yagpt)
	usage = resp.json()['result']['usage']['totalTokens']
	print(f'YAGPT использован: {usage} токенов || стоимость запроса: {0.4/1000*int(usage)} рублей')
	answer = resp.json()['result']['alternatives'][0]['message']['text']
	chat_history.append({'role': 'assistant', 'content': answer})
	yield answer
	save_chat_history(session, chat_history, userId, isTelegram)


@app.get('/get_conversation')
def get_conversation(
	session: Session = Depends(get_session),  # noqa: B008
	userId: str | None = Header(None),
	isTelegram: str | None = Header(None),
):
	chat_history = get_chat_history(session, userId, isTelegram)
	return {'chat_history': chat_history}


@app.post('/get_audio')
async def get_audio(req: TextPrompt):
	"""Receive text of GPT response, return file with audio"""
	filename = get_speech_from_gpt(text=req.text, voice=req.voice)
	return FileResponse(path=filename, media_type="audio/mpeg")


@app.post('/audio_prompt_to_text')
async def audio_prompt_to_text(audio: UploadFile = File(...)):  # noqa: B008
	"""Receive mp3 user audio, transcribe it to text"""
	with NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
		temp_file.write(await audio.read())
		temp_file_path = temp_file.name

	text = extract_text_from_audio(path=temp_file_path)

	temp_file.close()
	os.remove(temp_file_path)

	return {'text': text}


@app.post('/text_prompt')
async def text_prompt(
	prompt: TextPrompt,
	session: Session = Depends(get_session),  # noqa: B008
	req_ses: ReqSession = Depends(get_req_session),  # noqa: B008
	userId: str | None = Header(None),
	isTelegram: str | None = Header(None),
):
	"""Return GPT response to user text prompt"""
	chat_history = get_chat_history(session, userId, isTelegram)
	if prompt.llm == LLM.YANDEX:
		yagpt, chat_history = get_yagpt(
			text=prompt.text,
			chat_history=chat_history,
			native_lang=prompt.native_lang,
			foreign_lang=prompt.foreign_lang,
		)
		return StreamingResponse(
			stream_yagpt(yagpt, chat_history, req_ses, session, userId, isTelegram),
			media_type='text/plain',
		)
	return StreamingResponse(
		stream_gpt4all(model, chat_history, prompt.text, session, userId, isTelegram),
		media_type='text/plain',
	)


@app.delete('/reset_conversation')
def reset_conversation(
	session: Session = Depends(get_session),  # noqa: B008
	userId: str | None = Header(None),
	isTelegram: str | None = Header(None),
):
	delete_user(session, userId, isTelegram)
	return {'response': 'Successfully deleted'}


if __name__ == '__main__':
	uvicorn.run(app='main:app', host='localhost', port=8000, reload=True)
