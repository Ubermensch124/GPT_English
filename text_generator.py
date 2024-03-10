import random


def get_random_text() -> str:
    text = "Some text"
    with open('text.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        line_count = len(lines)
        random_sentence = random.randint(1, line_count)
        random_sentence = random_sentence-1 if random_sentence%2!=0 else random_sentence
        text = lines[random_sentence]
    return text
