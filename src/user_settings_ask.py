import logging

from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery

from src.user_settings import UserSettings

# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = Router(name=__name__)

user_settings_dict = {}

class UserSettingsAsk:
    """Кнопки для выбора настроек пользователя"""
    def __init__(self, user_id):
        self.user_id = user_id
        self.builder = InlineKeyboardBuilder()
        self.native_language = None
        self.studied_language = None
        self.studied_level = None

    def keyboard_settings(self):
        self.builder.button(text="Поменять настройки", callback_data="change")
        self.builder.button(text="Удалить настройки", callback_data="delete")
        self.builder.adjust(2, 1)
        return self.builder.as_markup()

    def generate_keyboard(self, options, callback_prefix):
        self.builder = InlineKeyboardBuilder()  # Обнуление билдера перед генерацией клавиатуры
        for option in options:
            self.builder.button(text=option[0], callback_data=f"{callback_prefix}_{option[1]}")
        self.builder.adjust(1, 3)
        return self.builder.as_markup()

@router.callback_query(F.data == "change")
async def change_settings(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_settings_handler = UserSettingsAsk(user_id)
    user_settings_dict[user_id] = user_settings_handler  # Сохраняем объект в словарь

    await callback_query.answer("Изменение настроек...")
    await callback_query.message.answer('Выбери свой родной язык',
                                        reply_markup=user_settings_handler.generate_keyboard(
                                            [("Русский", "ru"), ("Казахский", "kz"), ("Английский", "en")],
                                            "native_lang"))

@router.callback_query(lambda call: call.data.startswith("native_lang_"))
async def set_native_language(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_settings_handler = user_settings_dict.get(user_id)  # Получаем объект из словаря

    if not user_settings_handler:
        await callback_query.message.answer("Произошла ошибка. Попробуйте снова.")
        return

    user_settings_handler.native_language = callback_query.data.split("_")[-1].capitalize()
    logger.info("!!! native language: %s", user_settings_handler.native_language)
    await callback_query.message.answer('Выбери изучаемый язык',
                                        reply_markup=user_settings_handler.generate_keyboard(
                                            [("Английский", "en"), ("Русский", "ru"), ("Казахский", "kz")],
                                            "studied_lang"))

@router.callback_query(lambda call: call.data.startswith("studied_lang_"))
async def set_studied_language(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_settings_handler = user_settings_dict.get(user_id)

    if not user_settings_handler:
        await callback_query.message.answer("Произошла ошибка. Попробуйте снова.")
        return

    user_settings_handler.studied_language = callback_query.data.split("_")[-1].capitalize()
    logger.info("!!! studied language: %s", user_settings_handler.studied_language)
    await callback_query.message.answer('Выбери уровень владения изучаемого языка',
                                        reply_markup=user_settings_handler.generate_keyboard(
                                            [("Начальный", "beginner"), ("Средний", "intermediate"),
                                             ("Профессионал", "pro")], "level"))

@router.callback_query(lambda call: call.data.startswith("level_"))
async def save_user_settings(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_settings_handler = user_settings_dict.get(user_id)
    if not user_settings_handler:
        await callback_query.message.answer("Произошла ошибка. Попробуйте снова.")
        return

    user_settings_handler.studied_level = callback_query.data.split("_")[-1].capitalize()
    logger.info("!!! studied level: %s", user_settings_handler.studied_level)
    user_settings = UserSettings(user_id)

    user_settings.save(f"""Native language: {user_settings_handler.native_language}
    Studied language: {user_settings_handler.studied_language}
    Student level: {user_settings_handler.studied_level}
        """)

    await callback_query.message.answer("""
    🎉 Настройки сохранены! 🌟

    Отлично, теперь всё готово для эффективного обучения. 😊

    Что ты хочешь сделать дальше?

    Хочешь продолжить обучение? Давай начнем! 📚
    Есть вопросы или нужна помощь? Я всегда на связи, просто напиши! 📝
        """)


@router.callback_query(F.data == "delete")
async def delete_settings(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_settings = UserSettings(user_id)

    await callback_query.answer("Удаление настроек...")
    try:
        user_settings.delete()
        await callback_query.message.answer("Настройки удалены")
    except Exception as e:
        await callback_query.message.answer(f"Ошибка удаления настроек: {str(e)}")
