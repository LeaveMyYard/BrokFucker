import sqlite3
import os
import hashlib
import base64
from typing import Union
from datetime import datetime, timedelta
from lib.util.exceptions import RegistrationError, EmailValidationError
from lib.settings import Settings
from lib.email_sender import EmailSender
from threading import Timer
from lib.util.logger import init_logger

class DatabaseHandler:
    def __init__(self, file_name: str = 'database.db'):
        
        #Test if 'data' folder exists. If not, create it.
        directory = 'data'
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)

        #All database files will be located at data folder
        self.conn = sqlite3.connect(f'{directory}/{file_name}')
        self.cursor = self.conn.cursor()
        self.logger = init_logger(self.__class__.__name__)

    @staticmethod
    def init_tables():
        database = DatabaseHandler()
        script = 'lib/sql/init_tables.sql'
        database.logger.debug(f'Initializing database from `{script}` file...')

        #Load tables init sql request from 'lib/sql/init_tables.sql' and execute it. 
        request_file = open(script, mode='r')
        database.cursor.executescript(request_file.read())
        database.conn.commit()

    @staticmethod
    def run_verification_code_clearer(run_each: timedelta, duration_to_delete: timedelta):
        database = DatabaseHandler()
        database.logger.debug('Starting verification codes clearer.')
        database.logger.debug(f'Will run each {run_each} and remove codes that exist more then {duration_to_delete}')

        def __run_timer():
            database.clear_unused_codes(duration_to_delete)
            t = Timer(run_each.total_seconds(), __run_timer)
            t.start()

        __run_timer()

    @staticmethod
    def generage_new_random_hash() -> str:
        return base64.b32encode(
            hashlib.sha256(
                (
                    'random_words' + str(datetime.now())
                ).encode('utf-8')
            ).digest()
        ).decode('utf-8')

    def clear_unused_codes(self, duration_to_delete: timedelta):
        self.logger.info('Clearing unused verification codes...')
        self.cursor.execute(
            f"SELECT `verification_hash`, `request_date` FROM EmailVerification"
        )

        codes = 0
        for code, date in self.cursor.fetchall():
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            if (datetime.now() - date) > duration_to_delete:
                codes += 1
                self.cursor.execute(
                    f"DELETE FROM EmailVerification WHERE `verification_hash` = '{code}'"
                )
        
        self.logger.info(f'Clearing complete. Removed {codes} unused codes.')
        self.conn.commit()

    def check_user_exists(self, email: str) -> bool:
        '''
            Returns True if user with corresponding email exists, False otherwise
        '''

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchall()
        
        return res != []

    def check_password(self, email: str, password: str) -> bool:
        '''
            Return True if the email and password pair is correct.
            If password is incorrect, returns False
            If email is not registerd, will return False also.
        '''

        if not self.check_user_exists(email):
            return False

        self.cursor.execute(
            f"SELECT `password` FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchone()
        
        return res[0] == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def is_moderator(self, email: str) -> bool:
        if not self.check_user_exists(email):
            return False

        self.cursor.execute(
            f"SELECT `type` FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchone()

        return res[0] == 1

    def create_email_confirmation_request(self, email: str, password: str):
        '''
            Create new email verification request, generage new link for verification and send it via email.
        '''

        if self.check_user_exists(email):
            raise RegistrationError(-1200, 'Email is already in use.')

        if len(password) < 8:
            raise RegistrationError(-1201, 'A password size is less than 8.')

        if len(password) > 32:
            raise RegistrationError(-1201, 'A password size is bigger than 32.')

        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        random_hash = self.generage_new_random_hash()
        reg_date = datetime.now()

        self.cursor.execute(
            f"INSERT INTO EmailVerification (`email`, `password`, `verification_hash`, `request_date`)"
            f"VALUES ('{email}', '{password_hash}', '{random_hash}', '{reg_date}')"
        )        
        self.conn.commit()

        EmailSender.send_email_verification(email, random_hash)
        self.logger.debug(f'New email with confirmation code `{random_hash}` was sent to `{email}`')

    def verify_email_confirmation(self, code: str) -> Union[str, None]:
        '''
            If the corresponding email verification exist, create such user.
            If not - throws an exception
        '''

        self.cursor.execute(
            f"SELECT * FROM EmailVerification WHERE `verification_hash` = '{code}'"
        )

        on_failed = Settings.failed_email_verification_link()
        on_valid = Settings.vaild_email_verification_link()

        try:
            (_, email, password, date) = self.cursor.fetchone()
        except TypeError:
            raise EmailValidationError(-1204, 'No such verification code exists or it was already used.', on_failed)
        
        if (datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")) > timedelta(hours=24):
            raise EmailValidationError(-1203, 'Email verification time has passed.', on_failed)

        if self.check_user_exists(email):
            raise EmailValidationError(-1200, 'Email is already in use.', on_failed)
        
        self.logger.debug(f'New user `{email}` has successfuly confirmed his email and created an account')
        self.create_user(email, password)

        return on_valid

    def delete_email_confirmation_code(self, code):
        self.cursor.execute(
            f"DELETE FROM EmailVerification WHERE `verification_hash` = '{code}'"
        )
        self.conn.commit()

    def create_user(self, email: str, password: str) -> bool:
        '''
            This method will add a new user using email or password.
            If something is wrong, it will raise RegistrationError with the message of an error.
        '''

        reg_date = datetime.now()
        self.cursor.execute(
            f"INSERT INTO Users (`email`, `password`, `type`, `reg_date`)"
            f"VALUES ('{email}', '{password}', '0', '{reg_date}')"
        )
        self.conn.commit()

        self.logger.info(f'New user `{email}` was added.')

    def get_user_data(self, email) -> bool:
        if not self.check_user_exists(email):
            raise ValueError

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = '{email}'"
        )
        res = self.cursor.fetchone()

        return {
            'email': res[0],
            'type': 'moderator' if res[2] == 1 else 'user',
            'registration_date': res[3],
            'name': res[4],
            'phone_number': res[5]
        }

    def create_new_lot(
        self, 
        user,
        name,
        amount,
        currency,
        term,
        return_way,
        security,
        percentage,
        form
    ):
        date = datetime.now()
        self.cursor.execute(
            f"INSERT INTO Lots (`date`, `name`, `user`, `amount`, `currency`, `term`, `return_way`, `security`, `percentage`, `form`, `security_checked`, `guarantee_percentage`, `confirmed`)"
            f"VALUES ('{date}', '{name}', '{user}', '{amount}', '{currency}', '{term}', '{return_way}', '{security}', '{percentage}', '{form}', 'False', '0', 'False')"
        )

        self.cursor.execute(
            f"SELECT `id` FROM Lots WHERE `date` = '{date}'"
        )
        lot_id = self.cursor.fetchone()[0]

        self.cursor.execute(
            f"SELECT `user_lots` FROM UsersLots WHERE `email` = '{user}'"
        )
        
        res: list = eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.add(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `user_lots` = '{res}' WHERE `email` = '{user}'"
        )

        self.conn.commit()

        self.logger.info(f'New lot with id `{lot_id}` was created')

    def approve_lot(self, lot_id):
        self.cursor.execute(
            f"UPDATE Lots SET `confirmed` = 'True' WHERE `id` = '{lot_id}'"
        )
        self.conn.commit()
        self.logger.info(f'New lot with id `{lot_id}` was approved')

    def get_lot(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `id` = '{lot_id}'"
        )
        lot = self.cursor.fetchone()

        return {
            'id': lot[0],
            'date': lot[1],
            'name': lot[2],
            'user': lot[3],
            'amount': lot[4],
            'currency': lot[5],
            'term': lot[6],
            'return_way': lot[7],
            'security': lot[8],
            'percentage': lot[9],
            'form': lot[10],
            'security_checked': eval(lot[11]),
            'guarantee_percentage': lot[12]
        }

    def get_all_approved_lots(self):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `confirmed` = 'True'"
        )

        return [
            {
                'id': lot[0],
                'date': lot[1],
                'name': lot[2],
                'user': lot[3],
                'amount': lot[4],
                'currency': lot[5],
                'term': lot[6],
                'return_way': lot[7],
                'security': lot[8],
                'percentage': lot[9],
                'form': lot[10],
                'security_checked': eval(lot[11]),
                'guarantee_percentage': lot[12]
            }
            for lot in self.cursor.fetchall()
        ]

    def get_all_unapproved_lots(self):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `confirmed` = 'False'"
        )

        return [
            {
                'id': lot[0],
                'date': lot[1],
                'name': lot[2],
                'user': lot[3],
                'amount': lot[4],
                'currency': lot[5],
                'term': lot[6],
                'return_way': lot[7],
                'security': lot[8],
                'percentage': lot[9],
                'form': lot[10],
                'security_checked': eval(lot[11]),
                'guarantee_percentage': lot[12]
            }
            for lot in self.cursor.fetchall()
        ]

    def set_security_checked(self, lot_id, checked):
        self.cursor.execute(
            f"UPDATE Lots SET `security_checked` = '{checked}' WHERE `id` = '{lot_id}'"
        )
        self.conn.commit()
        self.logger.debug(f'`Security checked` flag on lot with id `{lot_id}` is set to `{checked}`')

    def add_lot_to_favorites(self, email, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = '{email}'"
        )

        res: list = eval(self.cursor.fetchone()[0])
        if lot_id not in res:
            res.append(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = '{res}' WHERE `email` = '{email}'"
        )
        self.conn.commit()

    def remove_lot_from_favorites(self, email, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = '{email}'"
        )
        
        res: list = eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.remove(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = '{res}' WHERE `email` = '{email}'"
        )
        self.conn.commit()

    def get_favorites(self, email):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = '{email}'"
        )
        
        res: list = eval(self.cursor.fetchone()[0])

        return [self.get_lot(lot_id) for lot_id in reversed(res)]