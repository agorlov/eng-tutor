import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.keyboards import Keyboards, start
from src.user_settings import UserSettings


# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = Router(name=__name__)

user_settings_dict = {}

@router.callback_query(F.data == "change")
async def change_settings(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_settings_handler = Keyboards(user_id)
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

    await callback_query.message.answer("""🎉 Настройки сохранены! 🌟

Отлично, теперь всё готово для эффективного обучения. 😊

Что ты хочешь сделать дальше?

Хочешь продолжить обучение? Давай начнем! 📚
Есть вопросы или нужна помощь? Я всегда на связи, просто напиши! 📝
        """, reply_markup=start)