
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
    `favorite_lots` TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (`email`) REFERENCES Users(`email`)
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

CREATE TABLE IF NOT EXISTS PasswordChangeVerification(
    `verification_hash` TEXT PRIMARY KEY,
    `email` TEXT NOT NULL,
    `password` TEXT NOT NULL,
    `request_date` DATETIME NOT NULL,
    FOREIGN KEY (`email`) REFERENCES Users(`email`)
);

CREATE TABLE IF NOT EXISTS AccountRestoreVerification(
    `verification_hash` TEXT PRIMARY KEY,
    `email` TEXT NOT NULL,
    `request_date` DATETIME NOT NULL,
    FOREIGN KEY (`email`) REFERENCES Users(`email`)
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
    `photos` TEXT DEFAULT '[]',
    FOREIGN KEY (`user`) REFERENCES Users(`email`)
);

CREATE TABLE IF NOT EXISTS LotsArchive (
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
    `photos` TEXT DEFAULT '[]',
    `original_id` INTEGER NOT NULL,
    `approve_date` DATETIME NOT NULL,
    FOREIGN KEY (`user`) REFERENCES Users(`email`)
);

CREATE VIEW IF NOT EXISTS ArchiveLatestLots
AS
	SELECT 
        ET1.`original_id` AS `id`, 
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
		`confirmed`,
		`deleted`,
		`commentary`,
		`photos`
	FROM `LotsArchive` AS ET1
	INNER JOIN (
		SELECT original_id, 
		MAX(approve_date) AS approve_date
		FROM `LotsArchive`
		GROUP BY original_id
	) AS ET2
	ON ET1.original_id = ET2.original_id
	AND ET1.approve_date = ET2.approve_date;

CREATE TRIGGER IF NOT EXISTS LotArchivation
AFTER UPDATE ON Lots
WHEN NEW.confirmed = 'True'
	BEGIN
        INSERT INTO LotsArchive(
            'date', 'name', 'user',
            'amount', 'currency', 'term',
            'return_way', 'security',
            'percentage', 'form', 'security_checked',
            'guarantee_percentage', 'confirmed',
            'deleted', 'commentary', 'photos',
            'original_id', 'approve_date'
        )
        VALUES (
            new.date, new.name, new.user,
            new.amount, new.currency, new.term,
            new.return_way, new.security,
            new.percentage, new.form, new.security_checked,
            new.guarantee_percentage, new.confirmed,
            new.deleted, new.commentary, new.photos,
            new.id, datetime('now')
        );
	END;

CREATE TABLE IF NOT EXISTS LotGuaranteeRequests (
    `id` INTEGER PRIMARY KEY,
    FOREIGN KEY (`id`) REFERENCES Lots(`id`)
);

CREATE VIEW IF NOT EXISTS LotsWithGuaranteeRequested 
AS
    SELECT *
    FROM `Lots`
    WHERE `id` IN (
        SELECT `id` FROM LotGuaranteeRequests
    );

CREATE TABLE IF NOT EXISTS LotSecurityVerificationRequests (
    `id` INTEGER PRIMARY KEY,
    FOREIGN KEY (`id`) REFERENCES Lots(`id`)
);

CREATE VIEW IF NOT EXISTS LotsWithSecurityVerificationRequested 
AS
    SELECT *
    FROM `Lots`
    WHERE `id` IN (
        SELECT `id` FROM LotSecurityVerificationRequests
    );

CREATE TABLE IF NOT EXISTS LotVerificationDeclines (
    `id` INTEGER PRIMARY KEY,
    `reason` TEXT NOT NULL,
    `removed_by` INTEGER NOT NULL,
    FOREIGN KEY (`id`) REFERENCES Lots(`id`),
    FOREIGN KEY (`removed_by`) REFERENCES Users(`email`)
);

CREATE VIEW IF NOT EXISTS LiveLots
AS
    SELECT *
    FROM Lots
    WHERE `confirmed` = 'True' 
    AND `deleted` = 'False'
	AND Lots.id NOT IN (
		SELECT `lot`
        FROM SubscriptionRequests
        WHERE `confirmed` = 'True'
        OR `finished` = 'True'
        GROUP BY `lot`
	);

CREATE VIEW IF NOT EXISTS LiveUnacceptedLots
AS
    SELECT *
    FROM Lots
    WHERE `confirmed` = 'False' AND `deleted` = 'False';

CREATE TABLE IF NOT EXISTS SubscriptionRequests (
    `id` TEXT PRIMARY KEY,
    `user` TEXT NOT NULL,
    `lot` INTEGER NOT NULL,
    `type` INTEGER NOT NULL,
    `message` TEXT,
    `confirmed` BOOLEAN NOT NULL DEFAULT 'False',
    `finished` BOOLEAN NOT NULL DEFAULT 'False'
);

CREATE VIEW IF NOT EXISTS ConfirmedLots
AS
    SELECT `lot`
    FROM SubscriptionRequests
    WHERE `confirmed` = 'True'
    AND `finished` = 'False'
    GROUP BY `lot`;

CREATE VIEW IF NOT EXISTS FinishedLots
AS
    SELECT `lot`
    FROM SubscriptionRequests
    WHERE `finished` = 'True'
    GROUP BY `lot`;

CREATE VIEW IF NOT EXISTS FinishedSubscriptions
AS
    SELECT `id`, `user`, `lot`, `type`, `message`
    FROM SubscriptionRequests
    WHERE `finished` = 'True' 
    AND `lot` IN (
        SELECT `id` 
        FROM Lots
        WHERE `deleted` = 'False'
    );

CREATE VIEW IF NOT EXISTS ConfirmedSubscriptions
AS
    SELECT `id`, `user`, `lot`, `type`, `message`
    FROM SubscriptionRequests
    WHERE `confirmed` = 'True'
    AND `finished` = 'False' 
    AND `lot` IN (
        SELECT `id` 
        FROM Lots
        WHERE `deleted` = 'False'
    );
    
CREATE VIEW IF NOT EXISTS UnconfirmedSubscriptions
AS
    SELECT `id`, `user`, `lot`, `type`, `message`
    FROM SubscriptionRequests
    WHERE `confirmed` = 'False'
    AND `lot` IN (
        SELECT `id` 
        FROM Lots
        WHERE `deleted` = 'False'
    )
    AND `lot` NOT IN ConfirmedLots;