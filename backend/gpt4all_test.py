from gpt4all import GPT4All

model = GPT4All(model_name="orca-mini-3b-gguf2-q4_0.gguf")


def get_model(chat_history=None):
    system_prompt = '### System:\nYou are an AI assistant that knows English extremely well. When user send you message you need to show him his grammatical mistakes.\n\n'
    prompt_template = '### User:\n{0}\n\n### Response:\n'
    model.config['systemPrompt'] = system_prompt
    model.config['promptTemplate'] = prompt_template
    return model
