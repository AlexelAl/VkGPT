import os
import openai
import wget
from config import Path, images_path

openai.api_key = os.getenv("OPENAI_API_KEY")


class ImageCreate:
    @staticmethod
    def get_url(prom):
        res = openai.Image.create(
            prompt=prom,
            n=1,
            size="512x512"
        )
        return res['data'][0]['url']

    @staticmethod
    def upload_image(prom, name):
        dir = Path(images_path, str(name) + '.png')
        wget.download(ImageCreate.get_url(prom), str(dir))
        return dir

    @staticmethod
    def delete_image(dir):
        os.remove(dir)
