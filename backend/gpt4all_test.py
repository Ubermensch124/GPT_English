import os

from credentials import (
	PROMPT_TEMPLATE,
	SYSTEM_PROMPT,
	SYSTEM_TEMPLATE,
	YANDEX_CATALOG_ID,
	YAPGT_API_KEY,
	GPT_MODEL,
)
from gpt4all import GPT4All
from requests import Request, Session


def get_model():
	model = GPT4All(
		model_name=GPT_MODEL,
		model_path='./ml_models',
		allow_download=False,
	)
	model.config['systemPrompt'] = SYSTEM_PROMPT
	model.config['promptTemplate'] = PROMPT_TEMPLATE
	return model


def get_yagpt(text, chat_history=None, native_lang='Русский язык', foreign_lang='English'):
	"""
	https://cloud.yandex.ru/ru/docs/yandexgpt/quickstart#api_1 - пример структуры ответа
	"""
	yagpt_prompt = {
		'modelUri': f'gpt://{YANDEX_CATALOG_ID}/yandexgpt-lite',
		'completionOptions': {'stream': False, 'temperature': 0.0, 'maxTokens': '500'},
		'messages': [
			{'role': 'system', 'text': SYSTEM_TEMPLATE[native_lang][foreign_lang]},
			{'role': 'user', 'text': text},
		],
	}

	if chat_history is not None:
		for message in chat_history:
			role, txt = message['role'], message['content']
			yagpt_prompt['messages'].append({'role': role, 'text': txt})
		yagpt_prompt['messages'].append({'role': 'user', 'text': text})
		chat_history.append({'role': 'user', 'content': text})
	else:
		chat_history = [
			{'role': 'system', 'content': SYSTEM_TEMPLATE[native_lang][foreign_lang]},
			{'role': 'user', 'content': text},
		]

	url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Api-Key {YAPGT_API_KEY}',
		'x-folder-id': f'{YANDEX_CATALOG_ID}',
	}

	req = Request('POST', url=url, headers=headers, json=yagpt_prompt)
	req = req.prepare()
	return req, chat_history


if __name__ == '__main__':
	s = Session()
	request = get_yagpt("Hello, what's your name?")
	resp = s.send(request=request, stream=True)
	i = 0
	flag = False
	for chunk in resp.iter_content(decode_unicode=True, chunk_size=5):
		if '\n' in chunk:
			flag = True
		elif flag and i < 12:
			i += 1
			continue
		else:
			print(chunk, end='\n')
