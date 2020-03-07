
CREATE TABLE IF NOT EXISTS Users (
    `email` TEXT PRIMARY KEY,
    `password` TEXT NOT NULL,
    `type` INTEGER NOT NULL DEFAULT '0',
    `reg_date` DATETIME NOT NULL,
    `name` TEXT DEFAULT NULL,
    `phone_number` TEXT DEFAULT NULL,
    `avatar` TEXT DEFAULT NULL
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
    NULL,
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
    SELECT *
    FROM Lots
    WHERE `confirmed` = 'True' AND `deleted` = 'False';

CREATE VIEW IF NOT EXISTS LiveUnacceptedLots
AS
    SELECT *
    FROM Lots
    WHERE `confirmed` = 'False' AND `deleted` = 'False';

CREATE TABLE IF NOT EXISTS SubscriptionRequests (
    `id` TEXT PRIMARY KEY,
    `user` TEXT NOT NULL,
    `lot` INTEGER NOT NULL,
    `confirmed` BOOLEAN NOT NULL DEFAULT 'False'
);

CREATE VIEW IF NOT EXISTS ConfirmedSubscriptions
AS
    SELECT `id`, `user`, `lot`
    FROM SubscriptionRequests
    WHERE `confirmed` = 'True' AND `lot` IN (
        SELECT `id` 
        FROM Lots
        WHERE `deleted` = 'False'
    );
    
CREATE VIEW IF NOT EXISTS UnconfirmedSubscriptions
AS
    SELECT `id`, `user`, `lot`
    FROM SubscriptionRequests
    WHERE `confirmed` = 'False' AND `lot` IN (
        SELECT `id` 
        FROM Lots
        WHERE `deleted` = 'False'
    );