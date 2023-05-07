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
from gpt.complete import *
from settings.delay import *
from settings.logger import *

from config import *


class App:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=TOKEN)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, GROUP_ID)
        self.uploader = VkUpload(self.vk_session)
        self.keyboard = VkKeyboard()
        self.keyboard.add_button(END_DIALOG_BTN, VkKeyboardColor.PRIMARY)
        self.keyboard = self.keyboard.get_keyboard()
        self.flood = Flood()
        self.conv = Conversation()

    @staticmethod
    def check_end_dialog(text):
        return text == END_DIALOG_BTN

    @staticmethod
    def check_image_prom(text):
        return len(text) >= len(IMAGE_KW) and text[:len(IMAGE_KW)] == IMAGE_KW

    @staticmethod
    def check_audio(event):
        return len(event.obj['message']['attachments']) != 0 and \
            event.obj['message']['attachments'][0]['type'] == 'audio_message'

    def sender(self, id=None, message=None, reply_to=None, keyboard=None, attachments=None):
        if attachments is None:
            attachments = []
        num = (len(message) + 4095) // 4096
        last = None
        for i in range(num):
            last = self.vk.messages.send(user_id=id,
                                         message=message[i * 4096:min(len(message), (i + 1) * 4096)],
                                         random_id=random.randint(0, 2 ** 64),
                                         reply_to=reply_to,
                                         keyboard=keyboard,
                                         attachment=''.join(attachments))
        return last

    def deleter(self, id=None, msg=None):
        self.vk_session.method('messages.delete', {'message_ids': [msg],
                                                   'peer_id': id,
                                                   'delete_for_all': 1})

    def gpt_answer(self, event, prom, reply_to):
        user = self.vk.users.get(user_ids=(event.obj.message['from_id']))[0]
        try:
            self.conv.add_state('user', prom, user['id'])
            ans = complete(self.conv.get_conv(user['id']))

            self.sender(event.obj.message['from_id'], ans, reply_to, self.keyboard)
            self.conv.add_state('assistant', ans, user['id'])
        except openai.error.RateLimitError as e:
            logger(str(e))
            self.sender(event.obj.message['from_id'],
                        COMPLETE_ERROR_MSG,
                        reply_to)
        except openai.error.InvalidRequestError:
            s_len = sum(map(lambda x: len(x['content']), self.conv.get_conv(user['id'])))
            self.conv.cut(user['id'], s_len - 4096)
            self.gpt_answer(event, prom, reply_to)

    def answer(self, event):
        user = self.vk.users.get(user_ids=(event.obj.message['from_id']))[0]
        prom = event.obj.message['text']
        reply_to = event.obj.message['id']

        del_id = self.sender(id=event.obj.message['from_id'],
                             message=GENERATING_MSG,
                             reply_to=reply_to)
        delay()
        self.gpt_answer(event, prom, reply_to)
        self.deleter(user['id'], del_id)

    def gpt_answer_image(self, event, prom, reply_to):
        try:
            dir = ImageCreate.upload_image(prom, event.obj.message['id'])
            upload_image = self.uploader.photo_messages(photos=str(dir))[0]
            att = ['photo{}_{}'.format(upload_image['owner_id'], upload_image['id'])]
            self.sender(event.obj.message['from_id'], IMAGE_SENT, reply_to, self.keyboard, att)
            ImageCreate.delete_image(dir)
        except openai.error.InvalidRequestError as e:
            logger(str(e))
            self.sender(event.obj.message['from_id'], IMAGE_ERROR_MSG, reply_to, self.keyboard)

    def answer_image(self, event):
        reply_to = event.obj.message['id']
        prom = event.obj.message['text'][len(IMAGE_KW):]
        del_id = self.sender(event.obj.message['from_id'],
                             GENERATING_MSG,
                             reply_to)
        self.gpt_answer_image(event, prom, reply_to)
        self.deleter(event.obj.message['from_id'], del_id)

    def handler_message(self, event):
        user = self.vk.users.get(user_ids=(event.obj.message['from_id']))[0]
        prom = event.obj.message['text']
        if App.check_end_dialog(prom):
            self.conv.delete_conv(user['id'])
            self.sender(user['id'], DIALOG_ENDED)
            return

        if App.check_image_prom(prom):
            self.answer_image(event)
            return

        if App.check_audio(event):
            text = Audio.transcribe(event.obj['message']['attachments'][0])
            event.obj['message']['text'] = text

        if not self.flood.check(user['id']):
            self.flood.update(user['id'])
            self.answer(event)
        else:
            self.sender(user['id'], FLOOD_WARN, reply_to=event.obj.message['id'])

    def handler_join(self, event):
        try:
            user = self.vk.users.get(user_ids=(event.obj['user_id']))[0]
            name = user['first_name'] + ' ' + user['last_name']
            self.sender(user['id'], HI_MESSAGE.format(name))
        except Exception as e:
            logger(str(e))

    def handler(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.handler_message(event)
        elif event.type == VkBotEventType.GROUP_JOIN:
            self.handler_join(event)

    def listen(self):
        for event in self.longpoll.listen():
            t = threading.Thread(target=self.handler, args=[event])
            t.start()

    def run(self):
        while True:
            try:
                self.listen()
            except Exception as e:
                logger(str(e))


if __name__ == '__main__':
    app = App()
    app.run()
