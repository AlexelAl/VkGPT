from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values("secret.env")

tk = config['OPENAI_API_KEY']
TOKEN = config['VK_TOKEN']

GROUP_ID = 220253752