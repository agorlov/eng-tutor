from .anna_db import AnnaDB


class UserSaved:
    '''Сохранение данных о пользователе в базу данных'''
    def __init__(self, db=None):
        if db is None:
            self.db = AnnaDB()
        else:
            self.db = db

    def save_user(self, user_id, username):
        conn = self.db.db()
        cur = conn.cursor()
        conn.autocommit = True

        cur.execute('''
                INSERT INTO users (telegram_id, username, registration_date, lastmessage) 
                VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
                ON CONFLICT (telegram_id) DO UPDATE
                SET lastmessage = CURRENT_TIMESTAMP;
            ''', (user_id, username))
