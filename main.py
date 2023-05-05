import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import threading
from settings.flood import Flood
from conversation import Conversation
from gpt.audio import Audio
from gpt.image_create import ImageCreate
from config import *
from gpt.complete import *
from settings.delay import *
from settings.logger import *

flood = Flood()
conv = Conversation()


def sender(vk, id=None, message=None, reply_to=None, keyboard=None, attachments=None):
    if attachments is None:
        attachments = []
    num = (len(message) + 4095) // 4096
    if num == 1:
        return vk.messages.send(user_id=id,
                                message=message,
                                random_id=random.randint(0, 2 ** 64),
                                reply_to=reply_to,
                                keyboard=keyboard,
                                attachment=''.join(attachments))
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


def gpt_answer(vk, event, prom, user, reply_to, keyboard):
    try:
        conv.add_state('user', prom, user['id'])
        ans = complete(conv.get_conv(user['id']))
        sender(vk, event.obj.message['from_id'], ans, reply_to, keyboard)
        conv.add_state('assistant', ans, user['id'])
    except openai.error.RateLimitError as e:
        logger(str(e))
        sender(vk, event.obj.message['from_id'],
               COMPLETE_ERROR_MSG,
               reply_to)


def gpt_image_answer(vk, event, prom, uploader, reply_to, keyboard):
    try:
        dir = ImageCreate.upload_image(prom, event.obj.message['id'])
        upload_image = uploader.photo_messages(photos=str(dir))[0]
        att = ['photo{}_{}'.format(upload_image['owner_id'], upload_image['id'])]
        sender(vk, event.obj.message['from_id'], IMAGE_SENT, reply_to, keyboard, att)
        ImageCreate.delete_image(dir)
    except openai.error.InvalidRequestError as e:
        logger(str(e))
        sender(vk, event.obj.message['from_id'], IMAGE_ERROR_MSG, reply_to, keyboard)


def answer(vk_session, event, user, reply_to, keyboard):
    vk = vk_session.get_api()
    prom = event.obj.message['text']
    del_id = sender(vk, id=event.obj.message['from_id'],
                    message=GENERATING_MSG,
                    reply_to=reply_to)
    delay()
    gpt_answer(vk, event, prom, user, reply_to, keyboard)
    deleter(vk_session, user['id'], del_id)


def answer_image(vk_session, event, keyboard, uploader, reply_to):
    vk = vk_session.get_api()
    prom = event.obj.message['text'][len(IMAGE_KW):]
    del_id = sender(vk, id=event.obj.message['from_id'],
                    message=GENERATING_MSG,
                    reply_to=reply_to)
    gpt_image_answer(vk, event, prom, uploader, reply_to, keyboard)
    deleter(vk_session, event.obj.message['from_id'], del_id)


def handler_msg(vk_session, event, keyboard, uploader):
    vk = vk_session.get_api()
    user = vk.users.get(user_ids=(event.obj.message['from_id']))[0]

    if event.obj.message['text'] == END_DIALOG_BTN:
        conv.delete_conv(user['id'])
        sender(vk, user['id'], DIALOG_ENDED, keyboard={})
        return

    if event.obj['message']['text'][:len(IMAGE_KW)] == IMAGE_KW:
        answer_image(vk_session, event, keyboard, uploader, event.obj.message['id'])
        return

    if len(event.obj['message']['attachments']) != 0 and\
            event.obj['message']['attachments'][0]['type'] == 'audio_message':
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
    uploader = VkUpload(vk_session)

    logger('Successfully logged')
    keyboard = VkKeyboard()
    keyboard.add_button(END_DIALOG_BTN, VkKeyboardColor.PRIMARY)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            t = threading.Thread(target=handler_msg, args=(vk_session, event, keyboard.get_keyboard(), uploader))
            t.start()
        if event.type == VkBotEventType.GROUP_JOIN:
            handler_join(vk_session, event)


if __name__ == '__main__':
    main()
