import logging
import aiohttp
import os
import re
import inflect

from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType

from src.agent_teacher import AgentTeacher
from config import TG_BOT_TOKEN, YANDEX_API_stt

# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Transcripted:
    def __init__(self, user_id, bot):
        self.bot = bot
        self.user_id = user_id
        self.model = model_repository.recognition_model()
        self.model.model = 'general'
        self.model.language = 'en-EN'
        self.model.audio_processing_type = AudioProcessingType.Full
        self.result = None
        self.inflect_engine = inflect.engine()

    async def download_file(self, message, agent):
        if not isinstance(agent, AgentTeacher):
            await message.answer('Распознавание недоступно. Введите текст.')
            return None

        file_url = await self._get_file_url(message.voice.file_id)
        if file_url is None:
            return None

        file_name = f"voice_{self.user_id}.ogg"
        if await self._save_file(file_url, file_name):
            return file_name
        return None

    async def _get_file_url(self, file_id):
        """Получение URL файла по его ID."""
        try:
            file_info = await self.bot.get_file(file_id)
            file_path = file_info.file_path
            return f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{file_path}"
        except Exception as e:
            logging.error(f"Error getting file URL: {e}")
            return None

    async def _save_file(self, file_url, file_name):
        """Сохранение файла по указанному URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status == 200:
                        with open(file_name, 'wb') as f:
                            f.write(await resp.read())
                        return True
                    else:
                        logging.error(f"Failed to download file, status code: {resp.status}")
                        return False
        except Exception as e:
            logging.error(f"Error saving file: {e}")
            return False

    def replace_numbers_with_text(self, text):
        """Замена чисел в тексте на текстовые представления."""
        return re.sub(r'\d+', self._number_to_words, text)

    def _number_to_words(self, match):
        """Конвертирование числа в текстовое представление."""
        number = match.group(0)
        return self.inflect_engine.number_to_words(number)

    async def transcription(self, audio_file_path, message):
        """Распознавание речи и обработка результата."""
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(api_key=YANDEX_API_stt)
        )
        try:
            self.result = self.model.transcribe_file(audio_file_path)
            return self.replace_numbers_with_text(str(self.result[0]))
        except Exception as e:
            logging.error(f"Error during recognition: {e}")
            await message.answer("Произошла ошибка при распознавании.")
        finally:
            self._cleanup(audio_file_path)

    def _cleanup(self, file_path):
        """Удаление временного файла."""
        if os.path.exists(file_path):
            os.remove(file_path)
