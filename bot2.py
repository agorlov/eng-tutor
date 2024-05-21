import logging
from traceback_with_variables import print_exc

from config import TG_BOT_TOKEN
from src.system_prompt_ru import GREETING

import telebot
from src.agent_main import AgentMain
from src.agent_translator import AgentTranslator
from src.agent_session_planner import AgentSessionPlanner
from src.agent_teacher import AgentTeacher
from src.agent_reviewer import AgentReviewer


# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

tg = telebot.TeleBot(TG_BOT_TOKEN)

# Словарь для хранения контекста
# user_id: { 'agent' : AgentMain, main_context: [], agents: {} }
# todo: переименовать в state
user_context = {}

def init_user_context(user_id):
    if user_id in user_context:
        return
    
    user_context[user_id] = {
        'agent': None,
        'main_context': [],
        'agents': {}
    }

    main = AgentMain(tg, user_context[user_id], user_id)

    user_context[user_id]['agent'] = main

    user_context[user_id]['agents'] = {
        'Main': main,        
        'Translator': AgentTranslator(tg, user_context[user_id], user_id),
        'Session Planner': AgentSessionPlanner(tg, user_context[user_id], user_id),
        'Teacher': AgentTeacher(tg, user_context[user_id], user_id),
        'Reviewer': AgentReviewer(tg, user_context[user_id], user_id),
        # Настройки, какой язык родной, какой целевой 
        # 'Settings' : 
    }

# /start
@tg.message_handler(commands=['start'])
def start(message):
    tg.send_message(message.chat.id, GREETING)


@tg.message_handler(func=lambda message: True)
def respond(message):
    user_id = message.chat.id
    logging.info(f"Rcv {user_id}: {message.text}")

    init_user_context(user_id)
    
    agent = user_context[user_id]['agent']
    agent.run(message.text)



tg.polling(none_stop=True)

# try:
#     tg.polling(none_stop=True)
# except Exception as e:
#     print_exc()
#     exit(1)
