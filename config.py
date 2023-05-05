from dotenv import load_dotenv, dotenv_values
import pathlib
from pathlib import Path

load_dotenv()
config = dotenv_values("secret.env")

tk = config['OPENAI_API_KEY']
TOKEN = config['VK_TOKEN']

GROUP_ID = 220253752

IMAGE_KW = '/image'

HI_MESSAGE = "Добро пожаловать, {}!\nЧтобы начать работу введите запрос, и искусственный интелект вам ответит"
COMPLETE_ERROR_MSG = 'Ошибка при получении данных с https://chat.openai.com\nПовторите попытку позже'
IMAGE_ERROR_MSG = 'Невозможно сгенерировать картинку по данному запросу'
GENERATING_MSG = "Ответ генерируется, подождите..."
FLOOD_WARN = "Не флуди"
END_DIALOG_BTN = 'Завершить предыдущий диалог'
DIALOG_ENDED = 'Диалог успешно завершён, можете начинать новый!'
IMAGE_SENT = 'Вот ваше изображение!'

audio_path = Path(pathlib.Path.cwd(), 'audio')
db_path = Path(pathlib.Path.cwd(), 'db', 'conv.sqlite')
images_path = Path(pathlib.Path.cwd(), 'images')