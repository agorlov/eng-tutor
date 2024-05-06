import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config import TG_BOT_TOKEN, DBCONN

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(TG_BOT_TOKEN)

# /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Hello! I'am Anna!")

# Run Anna
bot.polling(none_stop=True)