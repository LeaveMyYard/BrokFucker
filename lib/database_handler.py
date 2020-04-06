import sqlite3
import os
import hashlib
import base64
from typing import Union, Tuple
from flask import request
from datetime import datetime, timedelta
import lib.util.exceptions as APIExceptions
from lib.settings import Settings
from lib.email_sender import EmailSender
from threading import Timer
from lib.util.logger import init_logger
from lib.util.hash import sha256
from lib.settings import Settings
from werkzeug.utils import secure_filename
from PIL import Image
from os import path, remove
from datetime import datetime
from lib.util.enums import SubscriptionTypes

class DatabaseHandler:
    def __init__(self, file_name: str = 'database.db'):
        
        #Test if 'data' folder exists. If not, create it.
        directory = 'data'
        self.create_directory_if_not_exists(directory)

        #All database files will be located at data folder
        self.conn = sqlite3.connect(f'{directory}/{file_name}')
        self.cursor = self.conn.cursor()
        self.logger = init_logger(self.__class__.__name__)

    @staticmethod
    def create_directory_if_not_exists(directory):
        try:
            os.stat(directory)
        except:
            os.mkdir(directory)

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
                    f"DELETE FROM EmailVerification WHERE `verification_hash` = ?",
                    (code, )
                )

        self.cursor.execute(
            f"SELECT `verification_hash`, `request_date` FROM PasswordChangeVerification"
        )

        for code, date in self.cursor.fetchall():
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            if (datetime.now() - date) > duration_to_delete:
                codes += 1
                self.cursor.execute(
                    f"DELETE FROM PasswordChangeVerification WHERE `verification_hash` = ?",
                    (code, )
                )

        self.cursor.execute(
            f"SELECT `verification_hash`, `request_date` FROM AccountRestoreVerification"
        )

        for code, date in self.cursor.fetchall():
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            if (datetime.now() - date) > duration_to_delete:
                codes += 1
                self.cursor.execute(
                    f"DELETE FROM AccountRestoreVerification WHERE `verification_hash` = ?",
                    (code, )
                )

        
        self.logger.info(f'Clearing complete. Removed {codes} unused codes.')
        self.conn.commit()

    def check_user_exists(self, email: str) -> bool:
        '''
            Returns True if user with corresponding email exists, False otherwise
        '''

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = ?",
            (email, )
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
            f"SELECT `password` FROM Users WHERE `email` = ?",
            (email, )
        )
        res = self.cursor.fetchone()

        return res[0] == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def is_moderator(self, email: str) -> bool:
        if not self.check_user_exists(email):
            return False

        self.cursor.execute(
            f"SELECT `type` FROM Users WHERE `email` = ?",
            (email, )
        )
        res = self.cursor.fetchone()

        return res[0] >= 1

    def is_administrator(self, email: str) -> bool:
        if not self.check_user_exists(email):
            return False

        self.cursor.execute(
            f"SELECT `type` FROM Users WHERE `email` = ?",
            (email, )
        )
        res = self.cursor.fetchone()

        return res[0] >= 2

    def create_email_confirmation_request(self, email: str, password: str):
        '''
            Create new email verification request, generage new link for verification and send it via email.
        '''

        if self.check_user_exists(email):
            raise APIExceptions.RegistrationError(-1200, 'Email is already in use.')

        if len(password) < 8:
            raise APIExceptions.RegistrationError(-1201, 'A password size is less than 8.')

        if len(password) > 32:
            raise APIExceptions.RegistrationError(-1201, 'A password size is bigger than 32.')

        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        random_hash = self.generage_new_random_hash()
        reg_date = datetime.now()

        self.cursor.execute(
            f"INSERT INTO EmailVerification (`email`, `password`, `verification_hash`, `request_date`)"
            f"VALUES (?,?,?,?)",
            (email, password_hash, random_hash, reg_date)
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
            f"SELECT * FROM EmailVerification WHERE `verification_hash` = ?",
            (code, )
        )

        try:
            (_, email, password, date) = self.cursor.fetchone()
        except TypeError:
            raise APIExceptions.EmailValidationError(-1204, 'No such verification code exists, it was already used or was already deleted.')
        
        if (datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")) > timedelta(hours=24):
            raise APIExceptions.EmailValidationError(-1203, 'Email verification time has passed.')

        if self.check_user_exists(email):
            raise APIExceptions.EmailValidationError(-1200, 'Email is already in use.')
        
        self.logger.debug(f'New user `{email}` has successfuly confirmed his email and created an account')
        self.create_user(email, password)

    def delete_email_confirmation_code(self, code: str):
        self.cursor.execute(
            f"DELETE FROM EmailVerification WHERE `verification_hash` = ?",
            (code, )
        )
        self.conn.commit()

    def create_account_restore_email(self, email):
        if email == 'admin':
            raise APIExceptions.AccountRestoreError('Restoring the admin account is not possible.')

        if not self.check_user_exists(email):
            raise APIExceptions.AccountRestoreError('No such user exist.')

        random_hash = self.generage_new_random_hash()
        date = datetime.now()

        self.cursor.execute(
            f"INSERT INTO AccountRestoreVerification (`email`, `verification_hash`, `request_date`)"
            f"VALUES (?,?,?)",
            (email, random_hash, date)
        )
        self.conn.commit()

        EmailSender.send_account_restore_verification(email, random_hash)

    def verify_account_restore(self, code: str):
        '''
            If the corresponding email verification exist, create such user.
            If not - throws an exception
        '''

        self.cursor.execute(
            f"SELECT * FROM AccountRestoreVerification WHERE `verification_hash` = ?",
            (code, )
        )

        try:
            (_, email, date) = self.cursor.fetchone()
        except TypeError:
            raise APIExceptions.EmailValidationError(-1204, 'No such verification code exists, it was already used or was already deleted.')
        
        if (datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")) > timedelta(hours=24):
            raise APIExceptions.EmailValidationError(-1203, 'Email verification time has passed.')

        new_password = self.generage_new_random_hash()[:12]
        new_password_hashed = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

        self.cursor.execute(
            f"UPDATE Users SET `password` = ? WHERE `email` = ?",
            (new_password_hashed, email)
        )

        self.conn.commit()
        
        EmailSender.send_new_password(email, new_password)
        

    def create_email_for_user_password_change(self, email, new_password):
        if self.check_password(email, new_password):
            raise APIExceptions.PasswordChangeException("Your new password could not be the same, as your old password.")

        if len(new_password) < 8:
            raise APIExceptions.PasswordChangeException('A password size is less than 8.')

        if len(new_password) > 32:
            raise APIExceptions.PasswordChangeException('A password size is bigger than 32.')

        password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        random_hash = self.generage_new_random_hash()
        date = datetime.now()

        self.cursor.execute(
            f"INSERT INTO PasswordChangeVerification (`email`, `password`, `verification_hash`, `request_date`)"
            f"VALUES (?,?,?,?)",
            (email, password_hash, random_hash, date)
        )
        self.conn.commit()

        if email != 'admin':
            EmailSender.send_password_change_verification(email, random_hash)
            self.logger.debug(f'New password confirmation with code `{random_hash}` was sent to `{email}`')
        else:
            self.logger.warning(f'New password change requested for admin with code `{random_hash}`.')
            self.logger.warning(f'Go to "{request.host_url}{Settings.get_new_password_verification_link_base()}?code={random_hash}" to confirm it.')

    def verify_email_for_user_password_change(self, code: str):
        self.cursor.execute(
            f"SELECT * FROM PasswordChangeVerification WHERE `verification_hash` = ?",
            (code, )
        )

        try:
            (_, email, password, date) = self.cursor.fetchone()
        except TypeError:
            raise APIExceptions.EmailValidationError(-1204, 'No such verification code exists, it was already used or was already deleted.')
        else:
            if (datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")) > timedelta(hours=24):
                raise APIExceptions.EmailValidationError(-1203, 'Email verification time has passed.')

            self.cursor.execute(
                f"UPDATE Users SET `password` = ? WHERE `email` = ?",
                (password, email)
            )
            self.conn.commit()
        finally:
            self.delete_email_for_password_change_confirmation_code(code)

    def delete_email_for_password_change_confirmation_code(self, code: str):
        self.cursor.execute(
            f"DELETE FROM PasswordChangeVerification WHERE `verification_hash` = ?",
            (code, )
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
            f"VALUES (?, ?, '0', ?)",
            (email, password, reg_date)
        )
        self.conn.commit()

        self.logger.info(f'New user `{email}` was added.')

    def get_user_data(self, email) -> bool:
        if not self.check_user_exists(email):
            raise ValueError

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = ?",
            (email, )
        )
        res = self.cursor.fetchone()

        return {
            'email': res[0],
            'type': 'moderator' if res[2] == 1 else 'user',
            'registration_date': res[3],
            'name': res[4],
            'phone_number': res[5],
            'avatar': self.get_user_avatar_link(email)
        }

    def update_user_data(self, user, data, value):
        if not self.check_user_exists(user):
            raise ValueError

        # Data field is already checked, so no sql injection available
        self.cursor.execute(
            f"UPDATE Users SET `{data}` = ? WHERE `email` = ?",
            (value, user)
        )
        self.conn.commit()

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
        form,
        commentary
    ):
        date = datetime.now()
        self.cursor.execute(
            f"INSERT INTO Lots (`date`, `name`, `user`, `amount`, `currency`, `term`, `return_way`, `security`, `percentage`, `form`, `security_checked`, `guarantee_percentage`, `confirmed`, `commentary`)"
            f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'False', '0', 'False', ?)",
            (date, name, user, amount, currency, term, return_way, security, percentage, form, commentary)
        )

        self.cursor.execute(
            f"SELECT `id` FROM Lots WHERE `date` = ?",
            (date, )
        )
        lot_id = self.cursor.fetchone()[0]

        self.cursor.execute(
            f"SELECT `user_lots` FROM UsersLots WHERE `email` = ?",
            (user, )
        )
        
        res: list = eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.add(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `user_lots` = ? WHERE `email` = ?",
            (str(res), user)
        )

        self.conn.commit()

        self.logger.info(f'New lot with id `{lot_id}` was created')

        return lot_id

    def approve_lot(self, lot_id):
        if self.is_lot_removed_by_a_moderator(lot_id):
            self.remove_moderator_delete_reason(lot_id)

        self.cursor.execute(
            f"UPDATE Lots SET `confirmed` = 'True' WHERE `id` = ?",
            (lot_id, )
        )
        self.conn.commit()
        self.logger.info(f'New lot with id `{lot_id}` was approved')

    def get_user_display_name(self, user):
        data = self.get_user_data(user)
        return data['name'] or data['email']

    def set_user_avatar(self, user, image):
        self.create_directory_if_not_exists('data/images/temp')
        self.create_directory_if_not_exists('data/images/user')

        self.delete_user_avatar(user)

        temporary_file_location = f'data/images/temp/{secure_filename(image.filename)}'
        image.save(temporary_file_location)

        im = Image.open(temporary_file_location)
        photo_hash = sha256(str(datetime.now()))
        file_location = f'data/images/user/{photo_hash}.jpg'
        im = im.convert("RGB")
        im.save(file_location)

        self.cursor.execute(
            f"UPDATE Users SET `avatar` = ? WHERE `email` = ?",
            (photo_hash, user)
        )
        self.conn.commit()

        remove(temporary_file_location)

    def get_user_avatar_link(self, user):
        self.cursor.execute(
            f"SELECT `avatar` FROM Users WHERE `email` = ?",
            (user, )
        )
        photo_hash = self.cursor.fetchone()[0]
        file_location = f'data/images/user/{photo_hash}.jpg'

        try:
            open(file_location)
        except:
            return f'{request.host_url}image/user/default.jpg'
        else:
            return f'{request.host_url}image/user/{photo_hash}.jpg'

    def delete_user_avatar(self, user):
        self.cursor.execute(
            f"SELECT `avatar` FROM Users WHERE `email` = ?",
            (user, )
        )
        photo_hash = self.cursor.fetchone()[0]
        file_location = f'data/images/user/{photo_hash}.jpg'

        try:
            remove(file_location)
        except FileNotFoundError:
            return

        self.cursor.execute(
            f"UPDATE Users SET `avatar` = NULL WHERE `email` = ?",
            (user, )
        )
        self.conn.commit()

    def serialize_lot(self, lot: Tuple):
        res = {
            'id': lot[0],
            'date': lot[1],
            'name': lot[2],
            'user': lot[3],
            'user_display_name': self.get_user_display_name(lot[3]),
            'user_avatar': self.get_user_avatar_link(lot[3]),
            'amount': lot[4],
            'currency': lot[5],
            'term': lot[6],
            'return_way': lot[7],
            'security': lot[8],
            'percentage': lot[9],
            'form': lot[10],
            'security_checked': eval(lot[11]),
            'guarantee_percentage': lot[12],
            'commentary': lot[15],
            'photos': self.get_lot_photos(lot[0]),
            'taken': self.check_taken(lot[0])
        }
        
        if self.is_lot_removed_by_a_moderator(lot[0]):
            res['remove_reason'] = self.get_remove_reason(lot[0])

        res['verification_requested'] = self.check_lot_security_verification_requested(lot[0])
        res['club_guarantee_requested'] = self.check_club_guarantee_requested(lot[0])

        return res

    def set_lot_security_verification_requested(self, lot_id, requested: bool = True):
        if requested:
            self.cursor.execute(
                f"INSERT INTO LotSecurityVerificationRequests VALUES(?)",
                (lot_id, )
            )
        else:
            self.cursor.execute(
                f"DELETE FROM LotSecurityVerificationRequests WHERE `id` = ?",
                (lot_id, )
            )

        self.conn.commit()

    def check_lot_security_verification_requested(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM LotSecurityVerificationRequests WHERE `id` = ?",
            (lot_id,)
        )

        return self.cursor.fetchone() != []

    def set_lot_guarantee_requested(self, lot_id, requested: bool = True):
        if requested:
            self.cursor.execute(
                f"INSERT INTO LotGuaranteeRequests VALUES(?)",
                (lot_id, )
            )
        else:
            self.cursor.execute(
                f"DELETE FROM LotGuaranteeRequests WHERE `id` = ?",
                (lot_id, )
            )

        self.conn.commit()

    def check_club_guarantee_requested(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM LotGuaranteeRequests WHERE `id` = ?",
            (lot_id,)
        )

        return self.cursor.fetchone() != []

    def add_moderator_delete_reason(self, lot_id, moderator, reason):
        if self.is_lot_removed_by_a_moderator(lot_id):
            self.remove_moderator_delete_reason(lot_id)

        self.cursor.execute(
            f"INSERT INTO LotVerificationDeclines VALUES(?,?,?)",
            (lot_id, reason, moderator)
        )

        self.conn.commit()

    def remove_moderator_delete_reason(self, lot_id):
        self.cursor.execute(
            f"DELETE FROM LotVerificationDeclines WHERE `id` = ?",
            (lot_id, )
        )

        self.conn.commit()

    def is_lot_removed_by_a_moderator(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM LotVerificationDeclines WHERE `id` = ?",
            (lot_id, )
        )

        return self.cursor.fetchall() != []

    def get_remove_reason(self, lot_id):
        self.cursor.execute(
            f"SELECT `reason` FROM LotVerificationDeclines WHERE `id` = ?",
            (lot_id, )
        )

        return self.cursor.fetchone()[0]

    def check_taken(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM ConfirmedSubscriptions WHERE `lot` = ?",
            (lot_id, )
        )
        return self.cursor.fetchall() != []

    def get_lot(self, lot_id):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `id` = ?",
            (lot_id, )
        )
        lot = self.cursor.fetchone()

        return self.serialize_lot(lot)

    @staticmethod
    def __format_sql_lot_filter_string(lot_filter, where_is_already_used: bool = False) -> str:
        res = ""
        if lot_filter['show_only'] is not None:
            res += (' WHERE ' if not where_is_already_used else ' AND ') + ' AND '.join(
                [' OR '.join([f"`{type}` = '{value}'" for value in lot_filter['show_only'][type]]) for type in lot_filter['show_only']]
            )
        if lot_filter['order_by'] is not None:
            res += f" ORDER BY {lot_filter['order_by']} {lot_filter['order_type'] if lot_filter['order_type'] is not None else ''}"
        if lot_filter['limit'] is not None:
            res += f" LIMIT {lot_filter['limit']}"
        if lot_filter['offset'] is not None:
            res += f" OFFSET {lot_filter['offset']}"
        return res

    def get_all_approved_lots(self, lot_filter):
        self.cursor.execute(
            "SELECT * FROM LiveLots" + self.__format_sql_lot_filter_string(lot_filter)
        )

        return [self.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_all_unapproved_lots(self, lot_filter):
        self.cursor.execute(
            f"SELECT * FROM LiveUnacceptedLots" + self.__format_sql_lot_filter_string(lot_filter)
        )

        return [self.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def set_security_checked(self, lot_id, checked):
        self.cursor.execute(
            f"UPDATE Lots SET `security_checked` = ? WHERE `id` = ?",
            (checked, lot_id)
        )
        self.conn.commit()
        self.logger.debug(f'`Security checked` flag on lot with id `{lot_id}` is set to `{checked}`')

    def add_lot_to_favorites(self, email, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = ?",
            (email, )
        )

        res: list = eval(self.cursor.fetchone()[0])
        if lot_id not in res:
            res.append(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = ? WHERE `email` = ?",
            (str(res), email)
        )
        self.conn.commit()

    def remove_lot_from_favorites(self, email, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = ?",
            (email, )
        )
        
        res: list = eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.remove(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = ? WHERE `email` = ?",
            (str(res), email)
        )
        self.conn.commit()

    def get_favorites(self, email, lot_filter):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = ?" + self.__format_sql_lot_filter_string(lot_filter, where_is_already_used=True), 
            (email, )
        )
        
        res: list = eval(self.cursor.fetchone()[0])

        return [self.get_lot(lot_id) for lot_id in reversed(res)]

    def get_personal(self, email, lot_filter):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `user` = ? and `deleted` = 'False'" + self.__format_sql_lot_filter_string(lot_filter, where_is_already_used=True),
            (email, )
        )

        return [self.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_personal_deleted(self, email, lot_filter):
        self.cursor.execute(
            f"SELECT * FROM Lots WHERE `user` = ? and `deleted` = 'True'" + self.__format_sql_lot_filter_string(lot_filter, where_is_already_used=True),
            (email, )
        )

        return [self.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_lot_creator(self, lot_id):
        self.cursor.execute(
            f"SELECT `user` FROM Lots WHERE `id` = ?",
            (lot_id, )
        )

        return self.cursor.fetchone()[0]

    def delete_lot(self, lot_id):
        self.cursor.execute(
            f"UPDATE Lots SET `deleted` = 'True' WHERE `id` = ?",
            (lot_id, )
        )
        self.conn.commit()

    def restore_lot(self, lot_id):
        self.cursor.execute(
            f"UPDATE Lots SET `deleted` = 'False' WHERE `id` = ?",
            (lot_id, )
        )
        self.conn.commit()

    def update_data(self, lot_id, field, value):
        self.cursor.execute(
            f"UPDATE Lots SET `{field}` = ? WHERE `id` = ?",
            (value, lot_id)
        )
        self.conn.commit()

    @staticmethod
    def jsonify_photos(lot_id, photos):
        return {
            'lot_id': lot_id,
            'photos': [f'{request.host_url}image/lot/{photo}.jpg' for photo in photos]
        }

    def get_lot_photos_list(self, lot_id):
        self.cursor.execute(
            f"SELECT `photos` FROM Lots WHERE `id` = ?",
            (lot_id, )
        )

        return eval(self.cursor.fetchone()[0])

    def get_lot_photos(self, lot_id):
        return self.jsonify_photos(lot_id, self.get_lot_photos_list(lot_id))

    def add_photo(self, image, lot_id):
        self.create_directory_if_not_exists('data/images/temp')
        self.create_directory_if_not_exists('data/images/lots')

        temporary_file_location = f'data/images/temp/{secure_filename(image.filename)}'
        image.save(temporary_file_location)

        im = Image.open(temporary_file_location)
        photo_hash = sha256(str(datetime.now()))
        file_location = f'data/images/lots/{photo_hash}.jpg'
        im = im.convert("RGB")
        im.save(file_location)

        remove(temporary_file_location)

        self.cursor.execute(
            f"SELECT `photos` FROM Lots WHERE `id` = ?",
            (lot_id, )
        )
        photos = eval(self.cursor.fetchone()[0])
        photos.append(photo_hash)

        stringified_photos = str(photos).replace('\'', '"')

        self.cursor.execute(
            f"UPDATE Lots SET `photos` = ? WHERE `id` = ?",
            (stringified_photos, lot_id)
        )
        self.conn.commit()

        return 'Photo is successfuly added.'

    def remove_photo(self, lot_id, photo_id):
        self.cursor.execute(
            f"SELECT `photos` FROM Lots WHERE `id` = ?",
            (lot_id, )
        )
        photos: list = eval(self.cursor.fetchone()[0])
        photo_hash = photos.pop(photo_id)
        stringified_photos = str(photos).replace('\'', '"')

        remove(f'data/images/lots/{photo_hash}.jpg')

        self.cursor.execute(
            f"UPDATE Lots SET `photos` = ? WHERE `id` = ?",
            (stringified_photos, lot_id)
        )
        self.conn.commit()

        return 'Photo is successfuly removed.'

    def is_lot_in_archive(self, lot_id) -> bool:
        self.cursor.execute(
            f"SELECT `deleted` FROM Lots WHERE `id` = ?",
            (lot_id, )
        )

        return self.cursor.fetchone()[0] == 'True'

    def delete_lot_data(self, lot_id):
        self.cursor.execute(
            f"DELETE FROM LotVerificationDeclines WHERE `id` = ?",
            (lot_id, )
        )

        self.cursor.execute(
            f"DELETE FROM Lots WHERE `id` = ?",
            (lot_id, )
        )

        self.conn.commit()

    def user_has_phone_number(self, user):
        return self.get_user_data(user)['phone_number'] is not None

    def subscribe_user_to_lot(self, user, lot_id, type: SubscriptionTypes, message) -> bool:
        if type == SubscriptionTypes.PhoneCall and not self.user_has_phone_number(user):
            raise APIExceptions.UserHasNoPhoneNumber(user)

        id_hash = sha256(f'{user}_{lot_id}')
        try:
            self.cursor.execute(
                f"INSERT INTO SubscriptionRequests (`id`, `user`, `lot`, `type`, `message`) VALUES (?,?,?,?,?)",
                (id_hash, user, lot_id, type.value, message)
            )
            self.conn.commit()
            return True
        except:
            return False

    def unsubscribe_user_from_lot(self, user, lot_id):
        id_hash = sha256(f'{user}_{lot_id}')
        self.cursor.execute(
            f"DELETE FROM SubscriptionRequests WHERE `id` = ?",
            (id_hash, )
        )
        self.conn.commit()

    def get_user_subscriptions(self, user):
        self.cursor.execute(
            f"SELECT `lot`, `confirmed`, `type`, `message` FROM SubscriptionRequests WHERE `user` = ?",
            (user, )
        )
        return [{'lot': lot, 'type': SubscriptionTypes(type).name, 'message': message, 'confirmed': eval(confirmed)} for lot, confirmed, type, message in self.cursor.fetchall()]

    def get_approved_subscriptions(self):
        self.cursor.execute(
            f"SELECT * FROM ConfirmedSubscriptions"
        )
        return [{'id': id, 'user': user, 'lot': lot, 'type': SubscriptionTypes(type).name, 'message': message} for id, user, lot, type, message in self.cursor.fetchall()]

    def get_unapproved_subscriptions(self):
        self.cursor.execute(
            f"SELECT * FROM UnconfirmedSubscriptions"
        )
        return [{'id': id, 'user': user, 'lot': lot, 'type': SubscriptionTypes(type).name, 'message': message} for id, user, lot, type, message in self.cursor.fetchall()]

    def set_moderator_rights(self, email):
        self.cursor.execute(
            f"UPDATE Users SET `type` = 1 WHERE `user` = ?",
            (email, )
        )

        self.conn.commit()

    def remove_moderator_rights(self, email):
        self.cursor.execute(
            f"UPDATE Users SET `type` = 0 WHERE `user` = ?",
            (email, )
        )

        self.conn.commit()

    def set_lot_guarantee_value(self, lot_id, value):
        self.cursor.execute(
            f"UPDATE Users SET `guarantee_percentage` = ? WHERE `user` = ?",
            (value, lot_id)
        )

        self.conn.commit()

    def get_lots_with_guarantee_requested(self, lot_filter):
        self.cursor.execute(
            "SELECT * FROM LotsWithGuaranteeRequested" + self.__format_sql_lot_filter_string(lot_filter)
        )

        return [self.serialize_lot(lot) for lot in self.cursor.fetchall()]

    def get_lots_with_security_verification_requested(self, lot_filter):
        self.cursor.execute(
            "SELECT * FROM LotsWithSecurityVerificationRequested" + self.__format_sql_lot_filter_string(lot_filter)
        )

        return [self.serialize_lot(lot) for lot in self.cursor.fetchall()]