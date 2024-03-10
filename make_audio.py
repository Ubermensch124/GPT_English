import string
import random

import pyttsx3
from gtts import gTTS


def get_random_filename():
    chars = string.ascii_letters + string.digits
    filename = ''.join(random.choice(chars) for _ in range(15)) + '.ogg'
    return filename


def get_speech_from_pyttsx(text: str):
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Set the voice (0 for male, 1 for female)
    engine.setProperty('rate', 150)  # Set the speaking rate (words per minute)
    engine.setProperty('volume', 1.0)    # setting up volume level  between 0 and 1
    
    filename = get_random_filename()
    
    engine.save_to_file(text, filename)
    engine.runAndWait()
    
    return filename


def get_speech_from_gtts(text: str):
    filename = get_random_filename()

    tts = gTTS(text=text, lang='en')
    tts.save(filename)

    return filename
