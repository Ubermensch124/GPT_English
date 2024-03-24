import requests

from gpt4all import GPT4All

from credentials import YAPGT_API_KEY, YANDEX_CATALOG_ID


model = GPT4All(model_name="orca-mini-3b-gguf2-q4_0.gguf")


def get_model(chat_history=None):
    system_prompt = '### System:\nYou are an AI assistant that knows English extremely well. When user send you message you need to show him his grammatical mistakes.\n\n'
    prompt_template = '### User:\n{0}\n\n### Response:\n'
    model.config['systemPrompt'] = system_prompt
    model.config['promptTemplate'] = prompt_template
    return model


if __name__ == "__main__":
    yagpt_prompt = {
      "modelUri": f"gpt://{YANDEX_CATALOG_ID}/yandexgpt-lite",
      "completionOptions": {
        "stream": False,
        "temperature": 0.0,
        "maxTokens": "1000"
      },
      "messages": [
        {
          "role": "system",
          "text": "Найди ошибки в тексте и исправь их"
        },
        {
          "role": "user",
          "text": "Ламинат подойдет для укладке на кухне или в детской комнате – он не боиться влаги и механических повреждений благодаря защитному слою из облицованных меламиновых пленок толщиной 0,2 мм и обработанным воском замкам."
        }
      ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YAPGT_API_KEY}",
        "x-folder-id": f"{YANDEX_CATALOG_ID}"
    }

    response = requests.post(url, headers=headers, json=yagpt_prompt)
    print(response.status_code, response.content)
    if response.status_code < 400:
        result = response.text
        print(result)
        print()
        print(response)
