import string
import random
import os

import pyttsx3
from gtts import gTTS


def get_random_filename() -> str:
    """ Генерация рандомного имени для файла с синтезом речи """
    cur_dir = os.getcwd()
    chars = string.ascii_letters + string.digits
    path = cur_dir + '\\..\\shared\\'
    filename = path + ''.join(random.choice(chars) for _ in range(15)) + '.mp3'

    return filename


def get_speech_from_gtts(text: str) -> str:
    """ Синтез речи через google TTS """
    filename = get_random_filename()

    tts = gTTS(text=text, lang='en')
    tts.save(filename)

    return filename


def get_speech_from_pyttsx(text: str) -> str:
    """ Синтез речи через pyttsx3 """
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Set the voice (0 for male, 1 for female)
    engine.setProperty('rate', 150)  # words per minute
    engine.setProperty('volume', 1.0)    # between 0 and 1

    filename = get_random_filename()

    engine.save_to_file(text, filename)
    engine.runAndWait()

    return filename
