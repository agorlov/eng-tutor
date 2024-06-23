import logging
from .anna_db import AnnaDB

# Настраиваем логгер
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserSaved:
    '''Данные о пользователи сохранены в базу данных'''
    def __init__(self, db=None):
        if db is None:
            self.db = AnnaDB()
        else:
            self.db = db

    def save_user(self, user_id, username):
        conn = self.db.db()
        cur = conn.cursor()
        conn.autocommit = True

        try:
            cur.execute('''
                    INSERT INTO users (telegram_id, username, registration_date, lastmessage) 
                    VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
                    ON CONFLICT (telegram_id) DO UPDATE
                    SET lastmessage = CURRENT_TIMESTAMP;
                ''', (user_id, username))
        except Exception as e:
            logger.info("Error inserting data: %s", e)