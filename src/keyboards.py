from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Обычная клавиатура для старта урока
start = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Начать урок')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Нажимай на кнопку.',
    one_time_keyboard=True
)

syntez = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Озвучить')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

#syntez = InlineKeyboardMarkup(inline_keyboard=[
#    [InlineKeyboardButton(text='Озвучить', url='', callback_data='syntez')]
#])

class Keyboards:
    """Кнопки для выбора настроек пользователя"""
    def __init__(self, user_id):
        self.user_id = user_id
        self.builder = InlineKeyboardBuilder()
        self.native_language = None
        self.studied_language = None
        self.studied_level = None

    def keyboard_settings(self):
        self.builder.button(text="Поменять настройки", callback_data="change")
        #self.builder.button(text="Перейти к занятиям", callback_data="start_lessons")
        self.builder.adjust(2, 1)
        return self.builder.as_markup()

    def generate_keyboard(self, options, callback_prefix):
        self.builder = InlineKeyboardBuilder()  # Обнуление билдера перед генерацией клавиатуры
        for option in options:
            self.builder.button(text=option[0], callback_data=f"{callback_prefix}_{option[1]}")
        self.builder.adjust(1, 3)
        return self.builder.as_markup()