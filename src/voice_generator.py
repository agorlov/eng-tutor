import os
import logging
import requests
import subprocess

from aiogram.types import FSInputFile

from config import YANDEX_API_tts, YANDEX_catalog_Identifier

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceGenerator:
    def __init__(self, user_id, bot):
        self.user_id = user_id
        self.bot = bot
        self.iam_token = YANDEX_API_tts
        self.url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        self.folder_id = YANDEX_catalog_Identifier
        self.lang = 'en-EN'
        self.voice = 'john' #  https://yandex.cloud/ru/docs/speechkit/tts/voices
        self.raw_output_file = f'{self.user_id}_output.raw'
        self.opus_output_file = f'{self.user_id}_output.opus'

    def _generate_voice(self, text):
        headers = {
            'Authorization': 'Bearer ' + self.iam_token,
        }

        data = {
            'text': text,
            'lang': self.lang,
            'voice': self.voice,
            'folderId': self.folder_id,
            'format': 'lpcm',
            'sampleRateHertz': 48000,
        }

        try:
            with requests.post(self.url, headers=headers, data=data, stream=True) as resp:
                if resp.status_code != 200:
                    raise RuntimeError(f"Invalid response received: code: {resp.status_code}, message: {resp.text}")

                with open(self.raw_output_file, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=None):
                        f.write(chunk)
            logger.info("File '%s' has been created successfully.", self.raw_output_file)
            self._convert_raw_to_opus()

        except Exception as e:
            logger.info("Error during voice synthesis: %s", e)

    def _convert_raw_to_opus(self):
        try:
            command = [
                'ffmpeg',
                '-f', 's16le',  # Input format (raw PCM signed 16-bit little-endian)
                '-ar', '48000',  # Sample rate
                '-ac', '1',  # Number of channels
                '-i', self.raw_output_file,  # Input file
                '-c:a', 'libopus',  # Audio codec
                '-b:a', '64k',  # Bitrate
                self.opus_output_file  # Output file
            ]

            # Запуск команды и вывод лога
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"File '%s' has been created successfully.", self.opus_output_file)
            else:
                logger.error("Error executing ffmpeg command: %s", result.stderr)

        except subprocess.CalledProcessError as e:
            logger.error("Error executing command: %s", e)

        except Exception as e:
            logger.error("Error during file conversion: %s", e)

    def _cleanup(self, file_path):
        """Удаление временного файла."""
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_opus_file_path(self):
        """Возвращает путь к Opus-файлу."""
        return self.opus_output_file

    async def generate_and_send_voice(self, text):
        """Генерирует голосовое сообщение и отправляет его в чат."""
        self._generate_voice(text)

        opus_file_path = self.get_opus_file_path()

        if os.path.exists(opus_file_path):
            try:
                audio = FSInputFile(path=opus_file_path)
                await self.bot.send_audio(self.user_id, audio=audio)
                logger.info("!!! AUDIO FILE WAS SENT !!!")

            except Exception as e:
                logger.error("Error sending audio file: %s", e)
            finally:
                self._cleanup(self.raw_output_file)
                self._cleanup(opus_file_path)
        else:
            logger.error("File '%s' does not exist.", opus_file_path)
