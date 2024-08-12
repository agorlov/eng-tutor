import logging
from datetime import datetime
from .anna_db import AnnaDB

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhrasesRepetition:
    """
    Выбор фраз для повторения

    Attributes:
        user_id (int): ID пользователя.
        native_lang (str): Родной язык.
        studied_lang (str): Изучаемый язык.
        db (AnnaDB): Объект для работы с базой данных.

    Methods:
        save_phrases(self, connection, phrases): Сохраняет фразы пользователя в базе данных.
    """

    def __init__(self, user_id, native_lang, studied_lang, db=None):
        """
        Конструктор класса PhrasesSaved.

        Args:
            user_id (int): ID пользователя.
            native_lang (str): Родной язык.
            studied_lang (str): Изучаемый язык.
            db (AnnaDB, optional): Объект для работы с базой данных. Defaults to None.
        """
        self.user_id = user_id
        self.native_lang = native_lang
        self.studied_lang = studied_lang

        if db is None:
            self.db = AnnaDB()
        else:
            self.db = db


    def phrases(self, count = 3):
        """
        Выбирает фразы пользователя в базе данных.

        Выбирает фразы которые изучали ранее (не сегодня)

        Повторения должны быть завтра, через неделю, через две недели

        Args:
            count (int, optional): Количество фраз для выборки. Defaults to 3.

        """
        current_timestamp = datetime.now()
        cursor = self.db.db().cursor()   

        cursor.execute("""
            SELECT phrase
            FROM phrases
            WHERE user_id = %s
            AND native_lang = %s
            AND studied_lang = %s
            AND success_repetitions < 3
            AND first_success_repetition = FALSE
            AND (
                   (success_repetitions = 0 AND NOW() - INTERVAL '1 day' > last_repeat)
                OR (success_repetitions = 1 AND NOW() - INTERVAL '7 days' > last_repeat)
                OR (success_repetitions = 2 AND NOW() - INTERVAL '14 days' > last_repeat)
            )
            ORDER BY RANDOM()
            LIMIT %s;
            """,
            (self.user_id, self.native_lang, self.studied_lang, count)
        )

        result = cursor.fetchall()
        phrases = [row[0] for row in result]
        logger.info("Selected phrases: %s", phrases)

        return phrases

if __name__ == '__main__':
    psaved = PhrasesRepetition(user_id=425709869, native_lang='Russian', studied_lang='English')
    logger.info(psaved.phrases())
