import logging
import asyncio

from config import TG_BOT_TOKEN

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.agent_main import AgentMain
from src.agent_translator import AgentTranslator
from src.agent_session_planner import AgentSessionPlanner
from src.agent_teacher import AgentTeacher
from src.agent_archiver import AgentArchiver
from src.user_saved import UserSaved
from src.voice_handler import Voice_handler

# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создание образца класса
user_saved = UserSaved()
voice_handler = Voice_handler()

bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

# Словарь для хранения контекста
# user_id: { 'agent' : AgentMain, main_context: [], agents: {}, settings: {} }
# todo: переименовать в state
user_context = {}


def init_user_context(message: Message, user_id):
    if user_id in user_context:
        return

    user_context[user_id] = {
        'agent': None,
        'main_context': [],
        'agents': {},
        'settings': {}  # todo перенести код считывающий настройки из AgentMain (когда появится UserSettings)
    }

    user_context[user_id]['agents'] = {
        'Main': AgentMain(message, user_context[user_id], user_id),
        'Translator': AgentTranslator(message, user_context[user_id], user_id),
        'Session Planner': AgentSessionPlanner(message, user_context[user_id], user_id),
        'Teacher': AgentTeacher(message, user_context[user_id], user_id),
        'Archiver': AgentArchiver(message, user_context[user_id], user_id),
    }

    # Начинаем с агента Main
    user_context[user_id]['agent'] = user_context[user_id]['agents']['Main']


# /start
@dp.message(CommandStart())
async def start(message):
    user_language = message.from_user.language_code
    logger.info("!User Language: %s", user_language)

    if user_language == 'ru':
        await message.answer("""
🎉 Привет! Меня зовут Анна. 🌟

Я тут, чтобы помочь тебе освоить английский без скуки! 😊

Вот как это будет работать:
1. Я буду предлагать фразы, а ты - переводить их и запоминать, это как игра, которая научит тебя формулировать мысли на английском!
2. Если хочешь, можешь предложить свою тему для урока, и я с удовольствием поддержу. 📚
3. Нужен перевод? Просто напиши: "Переведи: твоя фраза или текст", и я на помощь! 📖
        """)
    else:
        await message.answer("""
🎉 Hi! My name is Anna. 🌟

I'm here to help you learn a foreign language without any boredom! 😊

Here's how it will work:
1. I will suggest phrases, and you will translate and memorize them. It's like a game that will teach you how to formulate thoughts in a foreign language!
2. If you want, you can suggest your own topic for the lesson, and I will gladly support you. 📚
3. Need a translation? Just write: "Translate: your phrase or text", and I’ll come to the rescue! 📖
        """)


@dp.message()
async def respond(message: Message):
    user_id = message.chat.id
    username = message.from_user.username

    #init_user_context(message, user_id)

    #  Обработка голоса
    if message.content_type == types.ContentType.VOICE:
        agent = user_context[user_id]['agent']
        audio_file_path = await voice_handler.download_file(user_id, message, bot, agent)

        if audio_file_path:
            audio_answer = await voice_handler.recognize(audio_file_path, message)

            logging.info(f"[Audio] Rcv {user_id}: {audio_answer}")

            init_user_context(audio_answer, user_id)

            await agent.run(audio_answer)

    #  Обработка текста
    elif message.content_type == types.ContentType.TEXT:
        logging.info(f"[Text] Rcv {user_id}: {message.text}")
        init_user_context(message, user_id)

        agent = user_context[user_id]['agent']
        await agent.run(message.text)

    user_saved.save_user(user_id, username)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
