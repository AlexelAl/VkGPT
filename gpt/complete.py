from config import tk
import openai


openai.api_key = tk


def complete(messages):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                              messages=messages)
    return completion.choices[0].message.content