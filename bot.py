import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from openai import OpenAI
import logging

from config import TG_BOT_TOKEN, DBCONN, OPENAI_API_KEY

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


bot = telebot.TeleBot(TG_BOT_TOKEN)
gpt = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = "You are GPT. Your name is Anna. Answer as concisely as possible."

# Словарь для хранения контекста
user_context = {}


# /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Hello! I'am Anna!")


@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_context[message.chat.id] = []
    bot.reply_to(message, "Контекст очищен.")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.chat.id
    logging.info(f"Rcv {user_id}: {message.text}")

    # Если контекст пуст, инициализируем его с системным сообщением
    if user_id not in user_context or not user_context[user_id]:
        user_context[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Добавляем новое сообщение пользователя в контекст
    user_context[user_id].append({"role": "user", "content": message.text})

    try:
        # Получаем ответ от OpenAI
        response = gpt.chat.completions.create(
            messages=user_context[user_id],
            model="gpt-3.5-turbo"
        )

        # Добавляем ответ от ассистента в контекст
        assistant_message = response.choices[0].message.content
        # logging.debug(response)
        user_context[user_id].append({"role": "assistant", "content": assistant_message})

        bot.reply_to(message, assistant_message)

        logging.info(f"Sent {user_id}: {assistant_message}")
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        bot.reply_to(message, f"Произошла ошибка при обращении к OpenAI API. Попробуйте позже.\n" + str(e))


# Run Anna
bot.polling(none_stop=True)
