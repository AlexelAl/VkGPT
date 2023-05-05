import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import threading
from flood import Flood
from conversation import Conversation
from audio import Audio
from config import *
from complete import *
from delay import *
from logger import *

flood = Flood()
conv = Conversation()


def sender(vk, id=None, message=None, reply_to=None, keyboard=None):
    num = (len(message) + 4095) // 4096
    if num == 1:
        return vk.messages.send(user_id=id,
                                message=message,
                                random_id=random.randint(0, 2 ** 64),
                                reply_to=reply_to,
                                keyboard=keyboard)
    for i in range(num):
        vk.messages.send(user_id=id,
                         message=message[i * 4096:min(len(message),
                                        (i + 1) * 4096)],
                         random_id=random.randint(0, 2 ** 64),
                         reply_to=reply_to,
                         keyboard=keyboard)


def deleter(vk_session, id=None, msg=None):
    vk_session.method('messages.delete', {'message_ids': [msg],
                                          'peer_id': id,
                                          'delete_for_all': 1})


def answer(vk_session, event, user, reply_to, keyboard):
    vk = vk_session.get_api()
    prom = event.obj.message['text']
    del_id = sender(vk, id=event.obj.message['from_id'],
                    message=GENERATING_MSG,
                    reply_to=reply_to)
    delay()
    try:
        conv.add_state('user', prom, user['id'])
        ans = complete(prom, conv.get_conv(user['id']))
        sender(vk, event.obj.message['from_id'], ans, reply_to, keyboard)
        conv.add_state('assistant', ans, user['id'])
    except openai.error.RateLimitError as e:
        logger(str(e))
        sender(vk, event.obj.message['from_id'],
               COMPLETE_ERROR_MSG,
               reply_to)

    deleter(vk_session, user['id'], del_id)


def handler_msg(vk_session, event, keyboard):
    vk = vk_session.get_api()
    user = vk.users.get(user_ids=(event.obj.message['from_id']))[0]
    if event.obj.message['text'] == 'Завершить предыдущий диалог':
        conv.delete_conv(user['id'])
        sender(vk, user['id'], 'Диалог успешно завершён, можете начинать новый!', keyboard={})
        return
    if len(event.obj['message']['attachments']) != 0 and event.obj['message']['attachments'][0]['type'] == 'audio_message':
        text = Audio.transcribe(event.obj['message']['attachments'][0])
        event.obj['message']['text'] = text
    if not flood.check(user['id']):
        flood.update(user['id'])
        answer(vk_session, event, user, event.obj.message['id'], keyboard)
    else:
        sender(vk=vk, id=user['id'],
               message=FLOOD_WARN,
               reply_to=event.obj.message['id'])


def handler_join(vk_session, event):
    vk = vk_session.get_api()
    user = vk.users.get(user_ids=(event.obj['user_id']))[0]
    name = user['first_name'] + ' ' + user['last_name']
    sender(vk, user['id'], HI_MESSAGE.format(name))


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    logger('Successfully logged')
    keyboard = VkKeyboard()
    keyboard.add_button('Завершить предыдущий диалог', VkKeyboardColor.PRIMARY)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            t = threading.Thread(target=handler_msg, args=(vk_session, event, keyboard.get_keyboard()))
            t.start()
        if event.type == VkBotEventType.GROUP_JOIN:
            handler_join(vk_session, event)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            logger(str(e))
            time.sleep(3)

# 1677610602
# 1677649963
