import os

import whisper
import warnings
warnings.simplefilter("ignore")


def extract_text_from_audio(path):
    """ 
    Принимает на вход путь до файла формата mp3.
    Возвращает транскрибированную аудиозапись.
    """
    model = whisper.load_model("tiny")
    result = model.transcribe(path, language="en")

    return result['text']
