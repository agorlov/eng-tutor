import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DBCONN


class AnnaDB:
    '''Соединение с базой данных'''
    def db(self):
        db = psycopg2.connect(
            dbname=DBCONN['dbname'],
            user=DBCONN['user'],
            password=DBCONN['password'],
            host=DBCONN['host'],
            port=DBCONN['port']
        )

        db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return db
        