
CREATE TABLE IF NOT EXISTS Users (
    `email` TEXT PRIMARY KEY,
    `password` TEXT NOT NULL,
    `type` INTEGER NOT NULL,
    `reg_date` DATETIME NOT NULL,
    `name` TEXT,
    `phone_number` TEXT
);

CREATE TABLE IF NOT EXISTS UsersFavoriteLots (
    `email` TEXT PRIMARY KEY,
    `LotIdsList` TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS Adding_user_to_favorites_list
AFTER INSERT ON Users
    BEGIN
        INSERT INTO UsersFavoriteLots
        VALUES (NEW.email, '[]');
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
    `security_checked` BOOLEAN NOT NULL,
    `guarantee_percentage` FLOAT NOT NULL,
    `confirmed` BOOLEAN NOT NULL
);