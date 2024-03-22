from gpt4all import GPT4All

model = GPT4All(model_name="orca-mini-3b-gguf2-q4_0.gguf")


# def get_response(current_prompt, chat_history=None):
#     """ 
#     Принимает на вход текст запроса от пользователя 
#     и предыдущую историю диалога.
#     Результат {
#         'response': ответ от бота, 
#         'chat_history': обновлённая история диалога
#     }
#     """
#     system_template = '''You are a excellent English teacher. User send to you a sentences and you need to find any grammatical mistakes in them and explain it to user.'''
#     prompt_template = 'USER: {0}\nASSISTANT: '

#     result = {"response": "", "chat_history": chat_history}
#     tokens = []

#     with model.chat_session(system_template, prompt_template):
#         if chat_history is not None:
#             model.current_chat_session = chat_history
#         for token in model.generate(prompt=current_prompt, streaming=True):
#             tokens.append(token)
#             print(token)
#         result['response'] = ''.join(tokens)
#         result['chat_history'] = model.current_chat_session

#     return result['response'], result['chat_history']


def get_model(chat_history=None):
    system_prompt = '### System:\nYou are an AI assistant that knows English extremely well. When user send you message you need to show him his grammatical mistakes.\n\n'
    prompt_template = '### User:\n{0}\n\n### Response:\n'
    model.config['systemPrompt'] = system_prompt
    model.config['promptTemplate'] = prompt_template
    return model
    # with model.chat_session(system_prompt, prompt_template):
    #     if chat_history is not None:
    #         model.current_chat_session = chat_history
    #     return model
