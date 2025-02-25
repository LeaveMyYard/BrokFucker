'''
    В этом модуле находятся все инструменты управления пользователями.
    Доступны два класса: User и UserRegistration.
'''

import ast
import hashlib
import sqlite3
from os import remove
from threading import Timer
from datetime import datetime, timedelta

from PIL import Image
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from flask import jsonify, request, make_response

import lib.util.exceptions as APIExceptions
from lib.settings import Settings
from lib.email_sender import EmailSender
from lib.util.enums import SubscriptionTypes
from lib.database_handler import DatabaseDrivenObject
from lib.util.hash import sha256, generage_random_hash

class User(DatabaseDrivenObject):
    '''
        Класс User представляет собой существующего пользователя.
        Возможно использование конструктора и почты,
        для получения объекта пользователя, или же
        User.current() для получения объекта текущего
        пользователя (того, который сделал запрос, если передались
        данные пользователя).
    '''

    auth = HTTPBasicAuth()
    login_required = auth.login_required

    @staticmethod
    @auth.verify_password
    def verify_user_password(email, password):
        '''
            Вызывается при проверке данных пользователя.
        '''

        try:
            user = User(email)
        except APIExceptions.UserError:
            return False
        else:
            return user.check_password(password)

    @staticmethod
    @auth.error_handler
    def unauthorized():
        '''
            Ответ в случае, если данные не верны.
        '''

        return make_response(
            jsonify({
                'code': -1002,
                'msg': 'You are not authorized to execute this request.'
            }), 403
        )

    @classmethod
    def current(cls):
        '''
            Возвращает текущего пользователя, который сделал запрос.
            (Если передались данные)
        '''

        return cls(cls.auth.username())

    def __init__(self, email: str):
        super().__init__()

        self.email = email

        if not self.exists():
            raise APIExceptions.UserError(f'No such user exists ({email}).')

    def check_password(self, password: str) -> bool:
        ''' Check if the password is correct

        Return True if the email and password pair is correct.
        If password is incorrect, returns False '''

        self.cursor.execute(
            f"SELECT `password` FROM Users WHERE `email` = ?",
            (self.email, )
        )
        res = self.cursor.fetchone()

        return res[0] == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def exists(self) -> bool:
        '''
            Проверяет, существует ли данный аккаунт.
        '''

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = ?",
            (self.email, )
        )
        res = self.cursor.fetchall()

        return res != []

    def restore_account(self):
        '''
            Отправляет письмо с подтвреждением восстановления аккаунта.
        '''

        if self.email == 'admin':
            raise APIExceptions.AccountRestoreError('Restoring the admin account is not possible.')

        random_hash = generage_random_hash()
        date = datetime.now()

        self.cursor.execute(
            f"INSERT INTO AccountRestoreVerification (`email`, `verification_hash`, `request_date`)"
            f"VALUES (?,?,?)",
            (self.email, random_hash, date)
        )
        self.conn.commit()

        EmailSender.send_account_restore_verification(self.email, random_hash)

    def get_data(self):
        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = ?",
            (self.email, )
        )
        res = self.cursor.fetchone()

        return {
            'email': res[0],
            'type': 'moderator' if res[2] == 1 else 'admin' if res[2] == 2 else 'user',
            'registration_date': res[3],
            'name': res[4],
            'phone_number': res[5],
            'avatar': self.get_avatar_link()
        }

    def get_display_name(self):
        data = self.get_data()
        return data['name'] or data['email']

    def edit_data(self, data, value):
        self.cursor.execute(
            f"UPDATE Users SET `{data}` = ? WHERE `email` = ?",
            (value, self.email)
        )
        self.conn.commit()

    def change_password(self, new_password):
        if self.check_password(new_password):
            raise APIExceptions.PasswordChangeException("Your new password could not be the same, as your old password.")

        if len(new_password) < 8:
            raise APIExceptions.PasswordChangeException('A password size is less than 8.')

        if len(new_password) > 32:
            raise APIExceptions.PasswordChangeException('A password size is bigger than 32.')

        password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        random_hash = generage_random_hash()
        date = datetime.now()

        self.cursor.execute(
            f"INSERT INTO PasswordChangeVerification (`email`, `password`, `verification_hash`, `request_date`)"
            f"VALUES (?,?,?,?)",
            (self.email, password_hash, random_hash, date)
        )
        self.conn.commit()

        if self.email != 'admin':
            EmailSender.send_password_change_verification(self.email, random_hash)
            self.logger.debug(
                'New password confirmation with code `%s` was sent to `%s`',
                random_hash,
                self.email
            )
        else:
            self.logger.warning(
                'New password change requested for admin with code `%s`.',
                random_hash)
            self.logger.warning(
                'Go to "%s%s?code=%s" to confirm it.',
                request.host_url,
                Settings.get_new_password_verification_link_base(),
                random_hash
            )

    def create_lot(
            self,
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
            (date, name, self.email, amount, currency, term, return_way, security, percentage, form, commentary)
        )

        self.cursor.execute(
            f"SELECT `id` FROM Lots WHERE `date` = ?",
            (date, )
        )
        lot_id = self.cursor.fetchone()[0]

        self.cursor.execute(
            f"SELECT `user_lots` FROM UsersLots WHERE `email` = ?",
            (self.email, )
        )

        res: list = ast.literal_eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.add(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `user_lots` = ? WHERE `email` = ?",
            (str(res), self.email)
        )

        self.conn.commit()

        self.logger.info(
            'New lot with id `%s` was created',
            lot_id
        )

        return lot_id

    def add_lot_to_favorites(self, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = ?",
            (self.email, )
        )

        res: list = ast.literal_eval(self.cursor.fetchone()[0])
        if lot_id not in res:
            res.append(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = ? WHERE `email` = ?",
            (str(res), self.email)
        )
        self.conn.commit()

    def remove_lot_from_favorites(self, lot_id):
        self.cursor.execute(
            f"SELECT `favorite_lots` FROM UsersLots WHERE `email` = ?",
            (self.email, )
        )

        res: list = ast.literal_eval(self.cursor.fetchone()[0])
        if lot_id in res:
            res.remove(lot_id)

        self.cursor.execute(
            f"UPDATE UsersLots SET `favorite_lots` = ? WHERE `email` = ?",
            (str(res), self.email)
        )
        self.conn.commit()

    def add_avatar(self, image):
        self.create_directory_if_not_exists('data/images/temp')
        self.create_directory_if_not_exists('data/images/user')

        self.delete_avatar()

        temporary_file_location = f'data/images/temp/{secure_filename(image.filename)}'
        image.save(temporary_file_location)

        im = Image.open(temporary_file_location)
        photo_hash = sha256(str(datetime.now()))
        file_location = f'data/images/user/{photo_hash}.jpg'
        im = im.convert("RGB")
        im.save(file_location)

        self.cursor.execute(
            f"UPDATE Users SET `avatar` = ? WHERE `email` = ?",
            (photo_hash, self.email)
        )
        self.conn.commit()

        remove(temporary_file_location)

    def get_avatar_link(self):
        self.cursor.execute(
            f"SELECT `avatar` FROM Users WHERE `email` = ?",
            (self.email, )
        )
        photo_hash = self.cursor.fetchone()[0]
        file_location = f'data/images/user/{photo_hash}.jpg'

        try:
            open(file_location)
        except OSError:
            return f'{request.host_url}image/user/default.jpg'
        else:
            return f'{request.host_url}image/user/{photo_hash}.jpg'

    def delete_avatar(self):
        self.cursor.execute(
            f"SELECT `avatar` FROM Users WHERE `email` = ?",
            (self.email, )
        )
        photo_hash = self.cursor.fetchone()[0]
        file_location = f'data/images/user/{photo_hash}.jpg'

        try:
            remove(file_location)
        except FileNotFoundError:
            return

        self.cursor.execute(
            f"UPDATE Users SET `avatar` = NULL WHERE `email` = ?",
            (self.email, )
        )
        self.conn.commit()

    def has_phone_number(self):
        return self.get_data()['phone_number'] is not None

    def subscribe_to_lot(self, lot_id: int, sub_type: str, message: str) -> bool:
        sub_type = SubscriptionTypes[sub_type]

        if sub_type == SubscriptionTypes.PhoneCall and not self.has_phone_number():
            raise APIExceptions.UserHasNoPhoneNumber(self.email)

        id_hash = sha256(f'{self.email}_{lot_id}')
        try:
            self.cursor.execute(
                f"INSERT INTO SubscriptionRequests (`id`, `user`, `lot`, `type`, `message`) VALUES (?,?,?,?,?)",
                (id_hash, self.email, lot_id, type.value, message)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def unsubscribe_from_lot(self, lot_id):
        id_hash = sha256(f'{self.email}_{lot_id}')
        self.cursor.execute(
            f"SELECT `confirmed` FROM SubscriptionRequests WHERE `id` = ?",
            (id_hash, )
        )

        res = self.cursor.fetchone()

        if res is None:
            raise APIExceptions.SubscriptionManagementError("Could not unsubscribe from lot, because you are not subscribed.")

        if res[0] == 'True':
            raise APIExceptions.SubscriptionManagementError("Could not unsubscribe from lot, because your subscription is already confirmed.")

        self.cursor.execute(
            f"DELETE FROM SubscriptionRequests WHERE `id` = ?",
            (id_hash, )
        )
        self.conn.commit()


class UserRegistrator(DatabaseDrivenObject):
    def begin_email_verification(self, email, password):
        '''
            Create new email verification request, generage new link for verification and send it via email.
        '''

        try:
            user = User(email)
        except APIExceptions.UserError:
            pass
        else:
            raise APIExceptions.RegistrationError('User already exists.')

        if len(password) < 8:
            raise APIExceptions.RegistrationError('A password size is less than 8.')

        if len(password) > 32:
            raise APIExceptions.RegistrationError('A password size is bigger than 32.')

        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        random_hash = generage_random_hash()
        reg_date = datetime.now()

        self.cursor.execute(
            f"INSERT INTO EmailVerification (`email`, `password`, `verification_hash`, `request_date`)"
            f"VALUES (?,?,?,?)",
            (email, password_hash, random_hash, reg_date)
        )
        self.conn.commit()

        EmailSender.send_email_verification(email, random_hash)
        self.logger.debug(
            'New email with confirmation code `%s` was sent to `%s`',
            random_hash,
            email
        )

    def verify_account_restore(self, code):
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
            raise APIExceptions.EmailValidationError('No such verification code exists, it was already used or was already deleted.')

        if (datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")) > timedelta(hours=24):
            raise APIExceptions.EmailValidationError('Email verification time has passed.')

        new_password = generage_random_hash()[:12]
        new_password_hashed = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

        self.cursor.execute(
            f"UPDATE Users SET `password` = ? WHERE `email` = ?",
            (new_password_hashed, email)
        )

        self.conn.commit()

        EmailSender.send_new_password(email, new_password)

    def verify_password_change(self, code):
        self.cursor.execute(
            f"SELECT * FROM PasswordChangeVerification WHERE `verification_hash` = ?",
            (code, )
        )

        try:
            (_, email, password, date) = self.cursor.fetchone()
        except TypeError:
            raise APIExceptions.EmailValidationError('No such verification code exists, it was already used or deleted.')
        else:
            if (datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")) > timedelta(hours=24):
                raise APIExceptions.EmailValidationError('Email verification time has passed.')

            self.cursor.execute(
                f"UPDATE Users SET `password` = ? WHERE `email` = ?",
                (password, email)
            )
            self.conn.commit()
        finally:
            self.delete_email_for_password_change_confirmation_code(code)

    def verify_email_confirmation(self, code: str):
        self.cursor.execute(
            f"SELECT * FROM EmailVerification WHERE `verification_hash` = ?",
            (code, )
        )

        try:
            (_, email, password, date) = self.cursor.fetchone()
        except TypeError:
            raise APIExceptions.EmailValidationError('No such verification code exists, it was already used or was already deleted.')

        if (datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")) > timedelta(hours=24):
            raise APIExceptions.EmailValidationError('Email verification time has passed.')

        try:
            User(email)
        except APIExceptions.UserError:
            pass
        else:
            raise APIExceptions.EmailValidationError('Email is already in use.')

        self.delete_email_confirmation_code(code)

        self.logger.debug(
            'New user `%s` has successfuly confirmed his email and created an account',
            email
        )
        self.create(email, password)

    def delete_email_confirmation_code(self, code: str):
        self.cursor.execute(
            f"DELETE FROM EmailVerification WHERE `verification_hash` = ?",
            (code, )
        )
        self.conn.commit()

    def delete_email_for_password_change_confirmation_code(self, code: str):
        self.cursor.execute(
            f"DELETE FROM PasswordChangeVerification WHERE `verification_hash` = ?",
            (code, )
        )
        self.conn.commit()

    def create(self, email, password):
        reg_date = datetime.now()
        self.cursor.execute(
            f"INSERT INTO Users (`email`, `password`, `type`, `reg_date`)"
            f"VALUES (?, ?, '0', ?)",
            (email, password, reg_date)
        )
        self.conn.commit()

        self.logger.info(
            'New user `%s` was added.',
            email
        )

    def run_verification_code_clearer(self, run_each: timedelta, duration_to_delete: timedelta):
        self.logger.debug('Starting verification codes clearer.')
        self.logger.debug(
            'Will run each %s and remove codes that exist more then %s',
            run_each,
            duration_to_delete
        )

        def __run_timer():
            self.__clear_unused_codes(duration_to_delete)
            self.__verification_timer = Timer(run_each.total_seconds(), __run_timer)
            self.__verification_timer.setDaemon(True)
            self.__verification_timer.start()

        __run_timer()

    def __clear_unused_codes(self, duration_to_delete: timedelta):
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


        self.logger.info(
            'Clearing complete. Removed %s unused codes.',
            codes
        )
        self.conn.commit()
