import logging
from datetime import datetime
from .anna_db import AnnaDB

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhrasesSaved:
    """
    Класс для сохранения записанных фраз.

    Attributes:
        user_id (int): ID пользовprintтеля.
        native_lang (str): Народная речь.
        studied_lang (str): Изучаемая речь.
        db (AnnaDB): Объект для работы с базой данных.

    Methods:
        save_phrases(self, connection, phrases): Сохраняет фразы пользователя в базе данных.
    """

    def __init__(self, user_id, native_lang, studied_lang, db=None):
        """
        Конструктор класса PhrasesSaved.

        Args:
            user_id (int): ID пользователя.
            native_lang (str): Народная речь.
            studied_lang (str): Изучаемая речь.
            db (AnnaDB, optional): Объект для работы с базой данных. Defaults to None.
        """
        self.user_id = user_id
        self.native_lang = native_lang
        self.studied_lang = studied_lang

        if db is None:
            self.db = AnnaDB()
        else:
            self.db = db


    def save_phrases(self, phrases):
        """
        Сохраняет фразы пользователя в базе данных.

        Args:
            phrases (list): Список словарей, содержащий информацию о фразах.
                Каждый элемент содержит следующие ключи:
                    phrase_orig (str): Непереведенная фраза.
                    phrase_translated (str): Переведенная фраза.
                    correct (bool): True, если фраза была правильно переведена.
        """
        current_timestamp = datetime.now()
        connection = self.db.db()

        with connection.cursor() as cursor:

            for phrase in phrases:
                phrase_orig = phrase['phrase_orig'].strip()
                phrase_translated = phrase['phrase_translated'].strip()
                correct = phrase['correct']


                cursor.execute("""
                    SELECT id, total_repetitions, success_repetitions
                    FROM phrases
                    WHERE user_id = %s AND phrase = %s
                    """,
                    (self.user_id, phrase_orig)
                )

                result = cursor.fetchone()

                if result:
                    phrase_id, total_repetitions, success_repetitions = result
                    total_repetitions += 1

                    if correct:
                        success_repetitions += 1

                    first_success_repetition = False
                    if total_repetitions == success_repetitions and total_repetitions > 0:
                        first_success_repetition = True

                    cursor.execute("""
                        UPDATE phrases
                        SET total_repetitions = %s,
                            success_repetitions = %s,
                            last_repeat = %s,
                            first_success_repetition = %s
                        WHERE id = %s
                        """,
                        (total_repetitions, success_repetitions, current_timestamp, first_success_repetition, phrase_id)
                    )
                else:

                    first_success_repetition = correct
                    logger.info("User ID: %s", self.user_id)
                    cursor.execute("""
                        INSERT INTO phrases (
                            user_id,
                            native_lang, 
                            studied_lang, 
                            phrase, 
                            translation,
                            total_repetitions, 
                            success_repetitions,
                            first_repeat,
                            last_repeat,
                            first_success_repetition
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (self.user_id, self.native_lang, self.studied_lang,
                        phrase_orig, phrase_translated, 1, 1 if correct else 0,
                        current_timestamp, current_timestamp, first_success_repetition)
                    )


if __name__ == '__main__':
    phrases = [
        {'phrase_orig': 'Phrase 1', 'phrase_translated': 'Phrase 1', 'correct': '1'}
    ]

    psaved = PhrasesSaved(user_id=1, native_lang='Russian', studied_lang='English')
    psaved.save_phrases(phrases)
