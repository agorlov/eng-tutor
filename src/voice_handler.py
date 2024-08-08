import logging
import aiohttp
import os
import re
import inflect

from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType

from src.agent_teacher import AgentTeacher
from config import TG_BOT_TOKEN, YANDEX_API


# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Voice_handler:
    def __init__(self):
        self.model = model_repository.recognition_model()
        self.model.model = 'general'
        #self.model.language = 'ru-RU'
        self.model.language = 'en-EN'
        self.model.audio_processing_type = AudioProcessingType.Full
        self.result = None

    async def download_file(self, user_id, message, bot, agent):
        if isinstance(agent, AgentTeacher):  # Проверка на то, что бы распознавание работало только в агенте Teacher
            file_id = message.voice.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            file_url = f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{file_path}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url) as resp:
                        if resp.status == 200:
                            file_name = f"voice_{user_id}.ogg"
                            with open(file_name, 'wb') as f:
                                f.write(await resp.read())
                            return file_name
            except Exception as e:
                logging.error(f"Error downloading file: {e}")
                return None
        else:
            await message.answer('Распознавание недоступно. Введите текст.')

    @staticmethod
    def replace_numbers_with_text(text):
        def replace_number(match):
            p = inflect.engine()
            number = match.group(0)
            return p.number_to_words(number)
        return re.sub(r'\d+', replace_number, text)

    async def recognize(self, audio_file_path, message):
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=YANDEX_API
            )
        )
        try:
            self.result = self.model.transcribe_file(audio_file_path)
            return self.replace_numbers_with_text(str(self.result[0]))
        except Exception as e:
            logging.error(f"Error during recognition: {e}")
            await message.answer("Произошла ошибка при распознавании.")
        finally:
            # Удаление временного файла после обработки
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
