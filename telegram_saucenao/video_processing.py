import io
import os
import cv2
from PIL import Image


class VideoFile:
    def __init__(self, bot, message, file_name):
        self.bot = bot
        self.message = message
        self.file_name = file_name

    def download_media(self):
        file_id_ = self.message.video.file_id
        file_info = self.bot.get_file(file_id_)
        downloaded_file = self.bot.download_file(file_info.file_path)

        self.check_folder(self.message.chat.id)

        with open(
            f"media/{self.message.chat.id}/{self.file_name}.mp4", "wb"
        ) as new_file:
            new_file.write(downloaded_file)

    def check_folder(self, chat_id):
        if not os.path.isdir("media"):
            os.mkdir("media")
        if not os.path.isdir(f"media/{chat_id}"):
            os.mkdir(f"media/{chat_id}")

    def prepare_file(self):
        vidObj = cv2.VideoCapture(f"media/{self.message.chat.id}/{self.file_name}.mp4")
        success, image = vidObj.read()
        vidObj.release()
        if not success:
            raise Exception('Failed to capture video file.')
        cv2.imwrite(f"media/{self.message.chat.id}/{self.file_name}.jpg", image)

        thumb_size = (250, 250)
        file_path = f"./media/{self.message.chat.id}/{self.file_name}.jpg"

        image = Image.open(file_path)
        image = image.convert("RGB")
        image.thumbnail(thumb_size, resample=Image.LANCZOS)
        image_data = io.BytesIO()
        image.save(image_data, format="PNG")
        files = {"file": (f"{self.file_name}.png", image_data.getvalue())}
        image_data.close()
        return files