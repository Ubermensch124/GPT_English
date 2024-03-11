import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, field_validator

from whisper_audio_extraction import extract_text_from_audio
from gpt4all_test import get_response
from make_audio import get_speech_from_gtts


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


app = FastAPI(title="GPTeacher", version="0.1")

@app.on_event('startup')
def startup():
    if not os.path.exists("../shared/"):
        os.mkdir("../shared/")


@app.post("/get_response_to_the_audio")
def get_gpt_response(chat_history: ChatHistory, path_to_user_audio: Path):
    """ 
    Принимает chat_history в виде json строки
    и путь до аудио-файла от пользователя. 
    """
    user_prompt = extract_text_from_audio(path=path_to_user_audio.path)
    gpt_text_answer, updated_chat_history = get_response(current_prompt=user_prompt, chat_history=chat_history.chat)
    gpt_audio_answer_path = get_speech_from_gtts(text=gpt_text_answer)
    return {
        "user_prompt": user_prompt,
        "gpt_text_answer": gpt_text_answer,
        "updated_chat_history": updated_chat_history,
        "gpt_audio_answer_path": gpt_audio_answer_path,
    }


if __name__=="__main__":
    uvicorn.run(app="main:app", host="localhost", port=8000)
