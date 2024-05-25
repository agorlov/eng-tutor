import logging
from traceback_with_variables import print_exc

from config import TG_BOT_TOKEN

import telebot
from src.agent_main import AgentMain
from src.agent_translator import AgentTranslator
from src.agent_session_planner import AgentSessionPlanner
from src.agent_teacher import AgentTeacher
from src.agent_archiver import AgentArchiver


# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

tg = telebot.TeleBot(TG_BOT_TOKEN)

# Словарь для хранения контекста
# user_id: { 'agent' : AgentMain, main_context: [], agents: {}, settings: {} }
# todo: переименовать в state
user_context = {}

def init_user_context(user_id):
    if user_id in user_context:
        return
    
    user_context[user_id] = {
        'agent': None,
        'main_context': [],
        'agents': {},
        'settings': {} # todo перенести код считывающий настройки из AgentMain (когда появится UserSettings)
    }

    user_context[user_id]['agents'] = {
        'Main': AgentMain(tg, user_context[user_id], user_id),
        'Translator': AgentTranslator(tg, user_context[user_id], user_id),
        'Session Planner': AgentSessionPlanner(tg, user_context[user_id], user_id),
        'Teacher': AgentTeacher(tg, user_context[user_id], user_id),
        'Archiver': AgentArchiver(tg, user_context[user_id], user_id),
    }

    # Начинаем с агента Main
    user_context[user_id]['agent'] = user_context[user_id]['agents']['Main']

# /start
@tg.message_handler(commands=['start'])
def start(message):
    tg.send_message(message.chat.id, """
🎉 Привет! Меня зовут Анна. 🌟

Я тут, чтобы помочь тебе освоить английский без скуки! 😊

Вот как это будет работать:
1. Я буду предлагать фразы, а ты - переводить их и запоминать, это как игра, которая научит тебя формулировать мысли на английском!
2. Если хочешь, можешь предложить свою тему для разговора, и я с удовольствием поддержу. 📚
3. Нужен перевод? Просто напиши: "Переведи: твоя фраза или текст", и я на помощь! 📖
    """)


@tg.message_handler(func=lambda message: True)
def respond(message):
    user_id = message.chat.id
    logging.info(f"Rcv {user_id}: {message.text}")

    init_user_context(user_id)
    
    agent = user_context[user_id]['agent']
    agent.run(message.text)


try:
    tg.polling(none_stop=True)
except Exception as e:
    print_exc()
    exit(1)
