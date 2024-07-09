import logging
import os

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserSettings:
    '''Настройки пользователя сохранены в текстовый файл'''

    def __init__(self, user_id):
        self.user_id = user_id

    def save(self, args):
        # Формируем путь к файлу настроек пользователя
        file_path = f'data/settings/{self.user_id}.txt'

        # Сохраняем строку настроек в файл
        with open(file_path, 'w') as file:
            file.write(args)

        logger.info("!Настройки пользователя %s сохранены в файле %s", self.user_id, file_path)

    def load(self):
        file_path = os.path.join("data", "settings", f"{self.user_id}.txt")
        try:
            with open(file_path, "r") as file:
                contents = file.read()
                return contents
        except FileNotFoundError:
            logger.info("!!!!Settings for user %s not found!!!!", self.user_id)
            return ""