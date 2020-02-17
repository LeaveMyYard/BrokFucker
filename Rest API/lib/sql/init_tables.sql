
CREATE TABLE IF NOT EXISTS Users (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `email` TEXT NOT NULL,
    `password` TEXT NOT NULL,
    `type` INTEGER NOT NULL,
    `reg_date` DATETIME NOT NULL,
    `name` TEXT,
    `phone_number` TEXT
);
