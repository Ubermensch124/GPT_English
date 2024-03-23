import json
import os
import logging
from contextlib import asynccontextmanager
from tempfile import NamedTemporaryFile
import shutil

import uvicorn
from fastapi import Depends, FastAPI, File, UploadFile, Header
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from whisper_audio_extraction import extract_text_from_audio
from gpt4all_test import get_model
from make_audio import get_speech_from_gtts
from database import Base, engine, Session
from models import WebUser

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



class TextPrompt(BaseModel):
    text: str
    
    
paths = ["http://localhost", "http://127.0.0.1"]
ports = [3000, 5173, 4173, 5500]
origins = [f'{path}:{port}' for port in ports for path in paths]

model = get_model()


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ on_startup alternative """
    Base.metadata.create_all(bind=engine)
    if os.path.exists("../shared"):
        shutil.rmtree("../shared")
    os.mkdir("../shared")
    yield

app = FastAPI(title="GPTeacher", version="0.1", lifespan=lifespan, log_config=logging.getLogger)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/get_audio")
async def get_audio(prompt: TextPrompt):
    filename = get_speech_from_gtts(text=prompt.text)
    return FileResponse(path=filename)


@app.post("/audio_prompt")
async def audio_prompt(audio: UploadFile = File(...)):
    with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(await audio.read())
        temp_file_path = temp_file.name

    text = extract_text_from_audio(path=temp_file_path)

    temp_file.close()
    os.remove(temp_file_path)

    return {"text": text}



async def stream_gpt(model, chat_history, prompt, session, userId):
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
    
    serialize_history = json.dumps(new_chat)
    to_delete = session.query(WebUser).filter(WebUser.chat_id == userId).first()
    if to_delete:
        session.delete(to_delete)
    new_obj = WebUser(chat_id=userId, chat_history=serialize_history)
    session.add(new_obj)
    session.commit()


@app.post("/text_prompt")
async def text_prompt(prompt: TextPrompt, session: Session = Depends(get_session), userId: str | None = Header(None)):
    res = session.query(WebUser).filter(WebUser.chat_id == userId).first()
    chat_history = None
    if res is not None:
        chat_history = json.loads(res.chat_history)
    
    return StreamingResponse(stream_gpt(model, chat_history, prompt.text, session, userId), media_type="text/plain")


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
