import logging
from .anna_db import AnnaDB

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserScore:
    """
    Скор пользователя
    """

    def __init__(self, user_id, db=None):
        self.user_id = user_id
        if db is None:
            self.db = AnnaDB()
        else:
            self.db = db

    def update_score(self, points):
        """
        Начисление очков за выполнение дела или за другие действия
        """

        cursor = self.db.db().cursor()
        cursor.execute("""
                INSERT INTO users (telegram_id, score)
                VALUES (%s, %s)
                ON CONFLICT (telegram_id) 
                DO UPDATE  SET score = users.score + EXCLUDED.score;
                """,
                       (self.user_id, points,))

        cursor.close()

    def stats(self):
        """
        Статистика по выученным фразам из таблицы phrases
        """

        cursor = self.db.db().cursor()
        cursor.execute("""
            SELECT 
                       COUNT(*) as phrases_count,
                       SUM(total_repetitions) as total_repetitions,
                       SUM(success_repetitions) as success_repetitions,
                       COUNT(*) FILTER (WHERE success_repetitions >= 3) as phrases_learned
            FROM phrases WHERE user_id = %s
        """, (self.user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return {
                'phrases_count': result[0],
                'total_repetitions': result[1],
                'success_repetitions': result[2],
                'phrases_learned': result[3]
            }
        else:
            return {
                'phrases_count': 0,
                'total_repetitions': 0,
                'success_repetitions': 0,
                'phrases_learned': 0
            }

    def user_score(self):
        """
        Скор пользователя
        """

        cursor = self.db.db().cursor()
        cursor.execute("SELECT score FROM users WHERE telegram_id = %s", (self.user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]
        else:
            return 0  # Default score if user not found


if __name__ == '__main__':
    UserScore(user_id=1).update_score(15)
    UserScore(user_id=1).update_score(15)
    logger.info("User 1 score: %s", UserScore(user_id=1).user_score())

    logger.info("Stats for user 425709869: %s", UserScore(user_id=425709869).stats())
