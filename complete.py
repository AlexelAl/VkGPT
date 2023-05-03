from config import tk
import openai


openai.api_key = tk


def complete(prom):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                              messages=[
                                                  {"role": "user",
                                                   "content": f"{prom}"}
                                              ])
    return completion.choices[0].message.content