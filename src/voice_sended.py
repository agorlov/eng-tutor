import os
import logging
import subprocess

from TTS.api import TTS
from aiogram.types import FSInputFile

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceSended:
    def __init__(self, user_id, bot):
        self.user_id = user_id
        self.bot = bot
        self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=False)
        self.wav_output_file = f'{self.user_id}_output.wav'
        self.opus_output_file = f'{self.user_id}_output.opus'

    def _generate_voice(self, text):
        self.tts.tts_to_file(text=text, file_path=self.wav_output_file)
        self._convert_wav_to_opus()

    def _convert_wav_to_opus(self):
        try:
            # Команда для конвертации
            command = [
                'ffmpeg',
                '-i', self.wav_output_file,  # Входной файл
                '-c:a', 'libopus',  # Кодек для OPUS
                '-b:a', '64k',  # Битрейт (по желанию)
                self.opus_output_file  # Выходной файл
            ]
            # Выполнение команды
            subprocess.run(command, check=True)
            logger.info(f'File has been created successfully: {self.opus_output_file}')
        except subprocess.CalledProcessError as e:
            logger.error(f'Error during file conversion: {e}')

    async def generate_and_send_voice(self, text):
        """Генерирует голосовое сообщение и отправляет его в чат."""
        self._generate_voice(text)
        if os.path.exists(self.opus_output_file):
            try:
                audio = FSInputFile(path=self.opus_output_file)
                await self.bot.send_audio(self.user_id, audio=audio)
                logger.info("!!! AUDIO FILE WAS SENT !!!")
            except Exception as e:
                logger.error("Error sending audio file: %s", e)
            finally:
                self._cleanup()

    def _cleanup(self):
        """Удаление временных файлов."""
        if os.path.exists(self.wav_output_file):
            os.remove(self.wav_output_file)
        if os.path.exists(self.opus_output_file):
            os.remove(self.opus_output_file)
