from datetime import datetime
import pytz

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import openai
import time
import threading
from config import *


openai.api_key = tk
next_using = time.time()


def logger(msg):
    with open('log.txt', 'a') as log:
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        dt = str(now.date()) + " " + str(now.hour).zfill(2) + ':' + str(now.minute).zfill(2)
        log.write(dt + '\n')
        log.write(msg + '\n\n')

def answer(vk_session, event, user, reply_to):
    global next_using
    vk = vk_session.get_api()
    prom = event.obj.message['text']
    del_id = vk.messages.send(user_id=event.obj.message['from_id'],
                              message="Ответ генерируется, подождите...",
                              random_id=random.randint(0, 2 ** 64),
                              reply_to=reply_to)

    if time.time() < next_using:
        next_using += 15
        time.sleep(next_using - time.time())
    else:
        next_using += 15

    try:
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                  messages=[
                                                      {"role": "user",
                                                       "content": f"{prom}"}
                                                  ])

        vk.messages.send(user_id=event.obj.message['from_id'],
                         message=completion.choices[0].message.content,
                         random_id=random.randint(0, 2 ** 64),
                         reply_to=reply_to)
    except openai.error.RateLimitError as e:
        logger(str(e))
        vk.messages.send(user_id=event.obj.message['from_id'],
                         message='Технические неполадки...\nПовторите попытку позже',
                         random_id=random.randint(0, 2 ** 64),
                         reply_to=reply_to)

    vk_session.method('messages.delete', {'message_ids': [del_id],
                                          'peer_id': user['id'],
                                          'delete_for_all': 1})


def func(vk_session, event):
    vk = vk_session.get_api()
    user = vk.users.get(user_ids=(event.obj.message['from_id']))[0]
    name = user['first_name'] + ' ' + user['last_name']

    answer(vk_session, event, user, event.obj.message['id'])


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    logger('Successfully logged')

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            t = threading.Thread(target=func, args=(vk_session, event))
            t.start()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            logger(str(e))
            time.sleep(3)
