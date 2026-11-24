-- База данных портала «Конференции.РФ» (SQLite)
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    login         VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL,
    phone         VARCHAR(20)  NOT NULL,
    email         VARCHAR(100) NOT NULL,
    role          VARCHAR(10)  NOT NULL DEFAULT 'user'
                  CHECK (role IN ('user', 'admin'))
);

CREATE TABLE rooms (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      VARCHAR(100) NOT NULL UNIQUE,
    room_type VARCHAR(30)  NOT NULL
              CHECK (room_type IN ('Аудитория', 'Коворкинг', 'Кинозал'))
);

CREATE TABLE bookings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    room_id        INTEGER     NOT NULL REFERENCES rooms (id),
    start_date     TEXT        NOT NULL,
    payment_method VARCHAR(30) NOT NULL
                   CHECK (payment_method IN ('При очном посещении', 'Перевод по СБП')),
    status         VARCHAR(30) NOT NULL DEFAULT 'Новая'
                   CHECK (status IN ('Новая', 'Мероприятие назначено', 'Завершено')),
    created_at     TEXT        NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE reviews (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL UNIQUE REFERENCES bookings (id) ON DELETE CASCADE,
    text       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

INSERT INTO rooms (name, room_type) VALUES
    ('Аудитория «Москва»', 'Аудитория'),
    ('Аудитория «Байкал»', 'Аудитория'),
    ('Коворкинг «Сириус»', 'Коворкинг'),
    ('Кинозал «Премьер»',  'Кинозал');