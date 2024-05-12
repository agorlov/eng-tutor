import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from openai import OpenAI
import logging

from config import TG_BOT_TOKEN, DBCONN, OPENAI_API_KEY, OPENAI_API_BASEURL
from src.system_prompt_ru import SYSTEM_PROMPT, GREETING

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.agent_boss import AgentBoss


# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


bot = telebot.TeleBot(TG_BOT_TOKEN)
gpt = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASEURL)



# Словарь для хранения контекста
user_context = {}


# /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, GREETING)


@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_context[message.chat.id] = []
    bot.reply_to(message, "Контекст очищен.")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.chat.id
    logging.info(f"Rcv {user_id}: {message.text}")
    
    boss = AgentBoss(gpt, user_context, user_id)

    response = boss.process_user_message(message.text)
    logging.info(f"Boss rsp {user_id}: {response}")
    bot.send_message(message.chat.id, response)    

    # try:        
    #     response = boss.process_user_message(message.text)
    #     logging.info(f"Boss rsp {user_id}: {assistant_message}")
    #     bot.send_message(message.chat.id, response)
    # except Exception as e:
    #     logging.error(f"Unexpected error: {e}")
    #     bot.reply_to(message, str(e))

# Run Anna
bot.polling(none_stop=True)
