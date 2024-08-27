import logging
import aiohttp
import os
import re
import inflect
import subprocess

from src.agent_teacher import AgentTeacher
from config import TG_BOT_TOKEN

# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Transcripted:
    """Считано голосовое сообщение пользователя"""
    def __init__(self, user_id, bot, whisper_model):
        self.bot = bot
        self.user_id = user_id
        self.model = whisper_model
        self.model_language = None
        self.inflect_engine = inflect.engine()


    async def download_file(self, message, agent, lang):
        """Скачивание и сохранение полученного голосового сообщения от пользователя"""
        self.model_language = lang.lower()
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
        """Сохранение файла по URL."""
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

    def _convert_ogg_to_wav(self, input_file, output_file):
        """Конвертация OGG в WAV."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-i', input_file, '-ar', '16000', '-ac', '1', output_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return True
            else:
                logging.error(f"ffmpeg error: {result.stderr}")
                return False
        except Exception as e:
            logging.error(f"Error during ffmpeg conversion: {e}")
            return False

    def replace_numbers_with_text(self, text):
        """Замена чисел в тексте на текстовые представления."""
        return re.sub(r'\d+', self._number_to_words, text)

    def _number_to_words(self, match):
        """Конвертирование числа в текстовое представление."""
        number = match.group(0)
        return self.inflect_engine.number_to_words(number)

    async def transcription(self, audio_file_path, message):
        audio_file_path_wav = f'{audio_file_path}.wav'
        try:
            # Конвертация OGG в WAV
            if not self._convert_ogg_to_wav(audio_file_path, audio_file_path_wav):
                await message.answer("Ошибка при конвертации аудиофайла в формат WAV.")
                return
            try:
                segments, info = self.model.transcribe(audio_file_path, language=self.model_language, beam_size=5)
                recognized_text = " ".join([segment.text for segment in segments])
                recognized_text = self.replace_numbers_with_text(recognized_text)
                # logging.info(f"Recognized text: {recognized_text}")
                return str(recognized_text)

            except Exception as e:
                logging.error(f"Error during recognition: {e}")
                await message.answer("Произошла ошибка при распознавании.")
        except Exception as e:
            logging.error(f"Error during file processing: {e}")
            await message.answer("Произошла ошибка при обработке аудиофайла.")
        finally:
            self._cleanup(audio_file_path, audio_file_path_wav)

    def _cleanup(self, file_path, file_path_wav):
        """Удаление временного файла."""
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(file_path_wav):
            os.remove(file_path_wav)
