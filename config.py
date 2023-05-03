from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values("secret.env")

tk = config['OPENAI_API_KEY']
TOKEN = config['VK_TOKEN']

GROUP_ID = 220253752

HI_MESSAGE = "Добро пожаловать, {}!\nЧтобы начать работу введите запрос, и искусственный интелект вам ответит"
COMPLETE_ERROR_MSG =  'Ошибка при получении данных с https://chat.openai.com/auth/login\nПовторите попытку позже'
GENERATING_MSG = "Ответ генерируется, подождите..."
