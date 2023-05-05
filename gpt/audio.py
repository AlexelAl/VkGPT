import os
import openai
import wget
from config import audio_path, Path

openai.api_key = os.getenv("OPENAI_API_KEY")


class Audio:
    @staticmethod
    def load(link, path):
        wget.download(link, str(path))

    @staticmethod
    def transcribe_file(path):
        audio_file = open(path, "rb")
        transcribe = openai.Audio.transcribe("whisper-1", audio_file)
        return transcribe['text']

    @staticmethod
    def transcribe(audio):
        link = audio['audio_message']['link_mp3']
        path = Path(audio_path,
                    str(audio['audio_message']['id']) + '.mp3')
        Audio.load(link, path)
        answer = Audio.transcribe_file(path)
        os.remove(path)
        return answer