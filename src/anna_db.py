import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DBCONN
from config import host, user, password


class AnnaDB:
    def __init__(self):
        self.user = DBCONN['user']
        self.password = DBCONN['password']
        self.host = DBCONN['host']
        self.dbname = DBCONN['dbname']

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
