import warnings

import whisper

warnings.simplefilter('ignore')


def extract_text_from_audio(path) -> str:
	"""
	Принимает на вход путь до файла формата mp3.
	Возвращает транскрибированную аудиозапись.
	"""
	model = whisper.load_model('base')
	result = model.transcribe(path, language='en')

	return result['text']
