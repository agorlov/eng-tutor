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
        
    # Создание базы данных
    def create_db(self):
        """ Соединение с базой данных """
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        try:
            cur.execute("CREATE USER anna WITH PASSWORD 'anna';")
        except psycopg2.ProgrammingError as e:
            print('User already exist')
        try:
            cur.execute("CREATE DATABASE " + self.dbname, f"OWNER {self.user};")
        except psycopg2.ProgrammingError as e:
            print("Database already exists")

        cur.close()
        conn.close()


        conn = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.dbname
        )
        
        cur = conn.cursor()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
        try:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS Phrases(
                    id SERIAL PRIMARY KEY,
                    -- user_id INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    native_lang TEXT NOT NULL,
                    studied_lang  TEXT NOT NULL,
                    phrase TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    total_repetitions INTEGER DEFAULT 0,
                    success_repetitions INTEGER DEFAULT 0,
                    first_repeat TIMESTAMP WITH TIME ZONE,
                    last_repeat TIMESTAMP WITH TIME ZONE
                );  
            ''')
            try:
                cur.execute('''CREATE INDEX idx_phrases_user_id ON phrases (user_id);''')
            except:
                print('Index idx_pharases_user_id already exist')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS Users(
                    telegram_id BIGINT PRIMARY KEY,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    lastname VARCHAR(55),
                    firstname VARCHAR(55),
                    username VARCHAR(255) UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    phone_number VARCHAR(20) UNIQUE,
                    lastmessage TIMESTAMP
                );
                ALTER TABLE users
                ADD COLUMN score INT DEFAULT 0;
                
                COMMENT ON COLUMN users.score IS 'Очки рейтинга пользователя';
            ''')
            # Проверка и добавление столбца user_id
            cur.execute('''
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name='Phrases' AND column_name='user_id';
                            ''')
            exists = cur.fetchone()
            if not exists:
                cur.execute('''
                                    ALTER TABLE Phrases ADD user_id BIGINT REFERENCES Users (telegram_id);
                                ''')
        except psycopg2.Error as e:
            print(f"Error creating tables or columns: {e}")

        cur.close()
        conn.close()




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
        