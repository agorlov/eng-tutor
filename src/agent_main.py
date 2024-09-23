import logging

from .func_gpt import FuncGPT
from .answer_switcher import AnswerSwitcher
from .user_score import UserScore

from src.user_settings import UserSettings

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ### Skill 1: Greeting and Introduction

# When the learner greets you, present the following options:

# - Learning Session: Propose starting a learning session.
# - Text Translation: Offer to translate any text they provide.

# If you don't know the settings, ask the user. And then save the settings by calling SWITCH Save Settings.
# Skill to be practiced: translation from Russian to English


MAIN_INSTRUCTION = """
# Ваша роль

Вы гений в изучении иностранных языков.
Вы также жизнерадостная девушка по имени Анна, которая предпочитает неформальное общение и любит шутить.
Всегда общайтесь с учеником на его родном языке, на котором он пишет вам или из настроек.

## Навыки

### Навык: Фасилитация обучения

Ваша задача — обязательно поприветствовать пользователя первым сообщением и предложить попрактиковаться.

Вы можете попрактиковаться:

Как только пользователь скажет, что хочет начать урок, убедитесь, что вы уже поприветствовали пользователя и предложили ему попрактиковаться или перевод, вы можете перенести разговор с помощью команды SWITCH Session Planner и передать настройки пользователя.

Вы должны ответить двумя способами:

1. С учеником — написать текст как обычно.
2. Чтобы переключиться на другого помощника — написать команду "SWITCH [Assistant Name]" в первой строке ответа. На следующей строке напишите инструкции для этого помощника.

Важно: не смешивайте текст для ученика и команду переключения.

### Навык: Настройки пользователя

Настройки пользователя выглядят так (каждый параметр на новой строке):
Native language: Ru
Studied language: En
Student level: intermediate

#### Ваши помощники

1. Планировщик сеансов — выбирает темы, определяет сложность и планирует сеансы. assistant_name="Session Planner"
2. Переводчик — помогает переводить тексты. assistant_name="Translator"

#### Переключение помощников

1. Начало обучения:
    - Когда пользователь выражает желание начать обучение, выясните, указаны ли настройки пользователя в правильном формате. Если он уже существует, он автоматически переключается на Планировщик сеансов без запроса подтверждения.
    - Предоставьте планировщику сеансов информацию о вашем родном и желаемом языке, а также об уровне владения языком.

2. Перевод текста:
    - Когда пользователь запрашивает перевод текста, автоматически переключайте эту задачу на переводчика, не запрашивая подтверждения.
    - Когда пользователь запрашивает перевод текста, строго отвечайте "SWITCH Translator".
    - Предоставьте переводчику текст для перевода и целевой язык.
    - Важная информация: НЕ переводите текст самостоятельно, просто автоматически переключайтесь на переводчика.

## Ограничения

    - Этот бот предназначен исключительно для изучения языка.
    - Все взаимодействия и задачи должны быть связаны с языковым образованием ученика.
    - Бот не обрабатывает необразовательные запросы или задачи, выходящие за рамки изучения и преподавания языка.
    - Общайтесь со учеником на его родном языке (родной язык). Если он еще не идентифицирован, говорите с ним на русском языке.

## Примеры ответов

### Приветствие и параметры

Здравствуйте! Какой язык вы изучаете сегодня? 😊

Привет! Хотите начать сеанс обучения? 🌟

### Переключение на Планировщик сессий

SWITCH Session Planner
Планирование сессии для студента с родным языком "En" и желаемым языком "Ru"
Уровень студента "intermediate", разговаривайте со студентом на его родном языке: русский

В этом случае мы знаем родной язык студента и язык, который он хочет изучать.

### Переключение на Переводчик

SWITCH Translator
На английский: Здравствуй!

"""


class AgentMain:
    def __init__(self, message, state, user_id):
        self.gpt = None  # FuncGPT(system=MAIN_INSTRUCTION)
        self.message = message
        self.state = state
        self.user_id = user_id
        self.u_settings = UserSettings(user_id)

    async def run(self, message):
        if self.gpt is None:
            await self.init_gpt()
            await self.show_stats()

        answer = self.gpt.chat(message)

        answ_sw = AnswerSwitcher(self.state, self.message, self.user_id)
        await answ_sw.switch(answer, self.state['agent'])

    def save_settings(self, *args, **kwargs):
        
        logger.info("SAVE SETTINGS CALLED")
        logger.info(args[0]['settings'])

        self.u_settings.save(args[0]['settings'])

        #self.init_settings()

        return "Настройки пользователя сохранены:\n " + args[0]['settings']


    def load_settings(self):
        """
        Reads the contents of a settings file for a given user ID.

        Args:
           user_id: The user ID for whom to read settings.

        Returns:
           A string containing the file contents, or None if the file doesn't exist.
        """
        logger.info(f"LOAD SETTINGS CALLED {self.user_id}")

        return self.u_settings.load()


    async def init_settings(self):
        """
        Initializes the user settings for a given user ID.

        1. Put them to current context as user message
        2. Put them to user state as setting

        """
        if 'settings' not in self.state or not self.state['settings']:
            try:
                settings = self.load_settings()

                if settings:
                    self.gpt.context.append({
                        "role": "user",
                        "content": "My preferences:\n" + settings
                    })
                    # Сохраним настройки в self.state, если они существуют
                    self.state['settings'] = self.settings_as_dict(settings)
                else:
                    logger.info("Настройки не найдены. Используем значения по умолчанию.")
            except ValueError as e:
                logger.error(f"ERROR READING SETTINGS FILE: {e}")
                self.u_settings.delete()
            except FileNotFoundError:
                logger.error("Файл настроек не найден.")

        '''
        try:
            settings = self.load_settings()

            if settings:
                self.gpt.context.append({
                    "role": "user",
                    "content": "My preferences:\n" + settings
                })
                # Сохраним настройки в self.state
                self.state['settings'] = self.settings_as_dict(settings)
                #await self.message.answer("Settings:\n" + settings)
            else:
                pass
                #await self.message.answer("Настройки не найдены. Создадим новые...")

        except ValueError as e:
            logger.error(f"ERROR READING SETTINGS FILE: {e}")
            self.u_settings.delete()
            #await self.message.answer("Файл настроек был поврежден и его пришлось удалить. Сейчас создадим новый...")

        except FileNotFoundError:
            logger.error("Файл настроек не найден.")
            try:
                self.u_settings.delete()
            except Exception as e:
                logger.error(f"Ошибка при удалении файла настроек: {e}")
            #await self.message.answer("Файл настроек не найден. Сейчас создадим новый...")
        '''

    async def show_stats(self):
        stats = ""

        statsdict = UserScore(self.user_id).stats()

        for param in statsdict:
            value = statsdict[param]
            stats += f"{param}: {value}\n"

        await self.message.answer(stats)

        return stats

    async def init_gpt(self):
        self.gpt = FuncGPT(system=MAIN_INSTRUCTION)

        await self.init_settings()

        '''
        self.gpt.add_func(
            {
                "type": "function",
                "function": {
                    "name": "save_settings",
                    "description": "Save user settings for language learning",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "settings": {
                                "type": "string",
                                "description": "Settings for language learning, as 4 strings: Native language, Studied language, Student level",
                            },
                        },
                        "required": ["settings"],
                    }
                }
            },
            self.save_settings
        )
        '''

    def settings_as_dict(self, settings: str) -> dict:
        result = {}

        # Разбиваем текст на строки и обрабатываем каждую строку
        for line in settings.strip().split('\n'):
            if line.strip():
                try:
                    # Разбиваем строку по символу ':'
                    key, value = line.split(':', 1)

                    # Удаляем лишние пробелы и добавляем в словарь
                    result[key.strip()] = value.strip()
                except:
                    raise ValueError(f"Line '{line}' is not in the correct format.")

        return result
