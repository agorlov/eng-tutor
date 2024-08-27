-- Users table
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INT DEFAULT 0,
    lastname VARCHAR(55),
    firstname VARCHAR(55),
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20) UNIQUE,
    lastmessage TIMESTAMP
);

COMMENT ON COLUMN users.score IS 'Очки рейтинга пользователя';