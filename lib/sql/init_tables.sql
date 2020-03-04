
CREATE TABLE IF NOT EXISTS Users (
    `email` TEXT PRIMARY KEY,
    `password` TEXT NOT NULL,
    `type` INTEGER NOT NULL DEFAULT '0',
    `reg_date` DATETIME NOT NULL,
    `name` TEXT,
    `phone_number` TEXT
);

CREATE TABLE IF NOT EXISTS UsersLots (
    `email` TEXT PRIMARY KEY,
    `user_lots` TEXT NOT NULL DEFAULT '[]',
    `favorite_lots` TEXT NOT NULL DEFAULT '[]'
);

CREATE TRIGGER IF NOT EXISTS AddingUserToUsersLots
AFTER INSERT ON Users
    BEGIN
        INSERT INTO UsersLots ('email')
        VALUES (NEW.email);
    END;

INSERT OR IGNORE INTO Users VALUES (
    'admin',
    '4e5587b9d3b8d5cd826883235ea4dbd43ff4551041b998b68c148fd5b85e5dc3',
    '2',
    '2020-02-24 00:50:24.262170',
    'Head Admin',
    NULL
);

CREATE TABLE IF NOT EXISTS EmailVerification (
    `verification_hash` TEXT PRIMARY KEY,
    `email` TEXT NOT NULL,
    `password` TEXT NOT NULL,
    `request_date` DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS Lots (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `date` DATETIME NOT NULL,
    `name` TEXT NOT NULL,
    `user` TEXT NOT NULL,
    `amount` TEXT NOT NULL,
    `currency` TEXT NOT NULL,
    `term` INTEGER NOT NULL,
    `return_way` INTEGER NOT NULL,
    `security` TEXT NOT NULL,
    `percentage` FLOAT NOT NULL,
    `form` INT NOT NULL,
    `security_checked` BOOLEAN NOT NULL DEFAULT 'False',
    `guarantee_percentage` FLOAT NOT NULL DEFAULT '0',
    `confirmed` BOOLEAN NOT NULL DEFAULT 'False',
    `deleted` BOOLEAN NOT NULL DEFAULT 'False',
    `commentary` TEXT DEFAULT '',
    `photos` TEXT DEFAULT '[]'
);

CREATE VIEW IF NOT EXISTS LiveLots
AS
    SELECT
        `id`,
        `date`,
        `name`,
        `user`,
        `amount`,
        `currency`,
        `term`,
        `return_way`,
        `security`,
        `percentage`,
        `form`,
        `security_checked`,
        `guarantee_percentage`,
        `commentary`
    FROM
        Lots
    WHERE
        `confirmed` = 'True' AND `deleted` = 'False';

CREATE VIEW IF NOT EXISTS LiveUnacceptedLots
AS
    SELECT
        `id`,
        `date`,
        `name`,
        `user`,
        `amount`,
        `currency`,
        `term`,
        `return_way`,
        `security`,
        `percentage`,
        `form`,
        `security_checked`,
        `guarantee_percentage`,
        `commentary`
    FROM
        Lots
    WHERE
        `confirmed` = 'False' AND `deleted` = 'False';