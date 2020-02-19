
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
    `deleted` BOOLEAN NOT NULL DEFAULT 'False'
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
        `guarantee_percentage`
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
        `guarantee_percentage`
    FROM
        Lots
    WHERE
        `confirmed` = 'False' AND `deleted` = 'False';

CREATE VIEW IF NOT EXISTS DeletedLots
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
        `guarantee_percentage`
    FROM
        Lots
    WHERE
        `deleted` = 'True';

CREATE INDEX IF NOT EXISTS UserLotsIndex ON Lots (
    `user`, `confirmed`, `deleted`, `date`
);