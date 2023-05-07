import random

from config import *
import vk_api

sending_message = """Уважаемые Пользователи!\n Вас приветствует команда разработчиков чат бота Chat GPT.\n
                    Бот был обновлён, в негобыл добавлен новый функционал, теперь он может\n
                    1) Работа с контекстом пользователя
                    2) Работа с аудио сообщениями
                    3) Создание изображений командой /image\n
                    Более подробно о новых возможностях вы можете прочитать в статье по ссылке https://vk.com/wall-220253752_1"""


def sender(vk, id=None, message=None, reply_to=None, keyboard=None, attachments=None):
    if attachments is None:
        attachments = []
    num = (len(message) + 4095) // 4096
    last = None
    for i in range(num):
        last = vk.messages.send(user_id=id,
                                message=message[i * 4096:min(len(message), (i + 1) * 4096)],
                                random_id=random.randint(0, 2 ** 64),
                                reply_to=reply_to,
                                keyboard=keyboard,
                                attachment=''.join(attachments))
    return last


vk_session = vk_api.VkApi(token=TOKEN)
users = vk_session.method('groups.getMembers', {'group_id': GROUP_ID})['items']
vk = vk_session.get_api()
print(users)
for i in users:
    try:
        sender(vk, i, sending_message)
    except Exception as e:
        print(e)
