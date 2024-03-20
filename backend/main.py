import json
import os
import logging
from contextlib import asynccontextmanager
from tempfile import NamedTemporaryFile

import uvicorn
from fastapi import Depends, FastAPI, File, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from whisper_audio_extraction import extract_text_from_audio
from gpt4all_test import get_response
from make_audio import get_speech_from_gtts
from database import Base, engine, Session
from models import WebUser

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ChatHistory(BaseModel):
    chat: list[dict] | None = None


class Path(BaseModel):
    path: str

    @field_validator('path')
    @classmethod
    def validate_path(cls, value: str):
        """ Проверяет, существует ли путь до аудио-файла """
        if not os.path.isfile(value):
            raise ValueError("File must exists")
        return value

paths = ["http://localhost", "http://127.0.0.1"]
ports = [3000, 5173, 4173, 5500]
origins = [f'{path}:{port}' for port in ports for path in paths]


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ on_startup alternative """
    if not os.path.exists("../shared/"):
        os.mkdir("../shared/")
    yield

app = FastAPI(title="GPTeacher", version="0.1", lifespan=lifespan, log_config=logging.getLogger)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/get_response_to_the_audio")
def get_gpt_response(chat_history: ChatHistory, path_to_user_audio: Path):
    """ 
    Принимает chat_history в виде json строки
    и путь до аудио-файла от пользователя. 
    """
    user_prompt = extract_text_from_audio(path=path_to_user_audio.path)
    gpt_text_answer, updated_chat_history = get_response(
        current_prompt=user_prompt,
        chat_history=chat_history.chat
    )
    gpt_audio_answer_path = get_speech_from_gtts(text=gpt_text_answer)
    return {
        "user_prompt": user_prompt,
        "gpt_text_answer": gpt_text_answer,
        "updated_chat_history": updated_chat_history,
        "gpt_audio_answer_path": gpt_audio_answer_path,
    }


@app.post("/get_audio")
async def get_audio(session: Session = Depends(get_session), audio: UploadFile = File(...), userId: str | None = Header(None)):
    """
    Тестирование работы фронтенда
    """
    res = session.query(WebUser).filter(WebUser.chat_id == userId).first()
    chat_history = None
    if res is not None:
        chat_history = json.loads(res.chat_history)

    with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(await audio.read())
        temp_file_path = temp_file.name

    text = extract_text_from_audio(path=temp_file_path)
    gpt_response, updated_chat = get_response(current_prompt=text, chat_history=chat_history)

    serialize_history = json.dumps(updated_chat)
    to_delete = session.query(WebUser).filter(WebUser.chat_id == userId).first()
    if to_delete:
        session.delete(to_delete)
    new_obj = WebUser(chat_id=userId, chat_history=serialize_history)
    session.add(new_obj)
    session.commit()

    temp_file.close()
    os.remove(temp_file_path)
    return {"GPTResponse": gpt_response, "UserPrompt": text}


@app.delete("/reset_conversation")
def delete_conv(session: Session = Depends(get_session), userId: str | None = Header(None)):
    to_delete = session.query(WebUser).filter(WebUser.chat_id == userId).first()
    if to_delete:
        session.delete(to_delete)
        session.commit()

    return {"response": "Successfully deleted"}


@app.get("/get_conversation")
def get_conv(session: Session = Depends(get_session), userId: str | None = Header(None)):
    user = session.query(WebUser).filter(WebUser.chat_id == userId).first()
    chat_history = None
    if user is not None:
        chat_history = json.loads(user.chat_history)

    return {"chat_history": chat_history}


if __name__=="__main__":
    uvicorn.run(app="main:app", host="localhost", port=8000, reload=True)