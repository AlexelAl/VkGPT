import os
import openai
import wget

openai.api_key = os.getenv("OPENAI_API_KEY")


class Audio:
    @staticmethod
    def load(link, name, format):
        wget.download(link, name + '.' + format)

    @staticmethod
    def transcribe_file(name, format):
        audio_file = open(name + '.' + format, "rb")
        transcribe = openai.Audio.transcribe("whisper-1", audio_file)
        return transcribe['text']

    @staticmethod
    def transcribe(audio):
        link = audio['audio_message']['link_mp3']
        name = 'audio\\' + str(audio['audio_message']['id'])
        format = 'mp3'
        Audio.load(link, name, format)
        answer = Audio.transcribe_file(name, format)
        os.remove(name + '.' + format)
        return answer