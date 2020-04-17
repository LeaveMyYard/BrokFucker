from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatabaseHandler
from flask import Flask, abort, jsonify, request, make_response
from lib.util.exceptions import EmailValidationError
from lib.util.hash import sha256, generage_random_hash
from lib.settings import Settings
from werkzeug.utils import secure_filename
from PIL import Image
from os import path, remove
from lib.util.enums import SubscriptionTypes
import sqlite3

from lib.database_handler import DatabaseDrivenObject
import lib.util.exceptions as APIExceptions
import hashlib
from datetime import datetime, timedelta
from lib.email_sender import EmailSender

class User(DatabaseDrivenObject):
    auth = HTTPBasicAuth()
    login_required = auth.login_required

    @staticmethod
    @auth.verify_password
    def verify_user_password(email, password):
        database = DatabaseHandler()
        return database.check_password(email, password)

    @staticmethod
    @auth.error_handler
    def unauthorized():
        return make_response(jsonify({'code': -1002, 'msg': 'You are not authorized to execute this request.'}), 403)

    @classmethod
    def current(cls):
        return User(cls.auth.username())

    def __init__(self, email: str):
        self.email = email

        if not self.exists():
            raise APIExceptions.UserError('No such user exists.')

    def exists(self) -> bool:
        '''
            Returns True if user with corresponding email exists, False otherwise
        '''

        self.cursor.execute(
            f"SELECT * FROM Users WHERE `email` = ?",
            (self.email, )
        )
        res = self.cursor.fetchall()
        
        return res != []

    def restore_account(self):
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

    @staticmethod
    def get_data():
        database = DatabaseHandler()
        res = database.get_user_data(User.email())
        return res

    @staticmethod
    def edit_data(data, value):
        database = DatabaseHandler()
        database.update_user_data(User.email(), data, value)

    @staticmethod
    def change_password(new_password):
        database = DatabaseHandler()
        database.create_email_for_user_password_change(User.email(), new_password)

    @staticmethod
    def verify_password_change(code):
        database = DatabaseHandler()
        database.verify_email_for_user_password_change(code)

    @staticmethod
    def create_lot(
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
        database = DatabaseHandler()
        return database.create_new_lot(
            User.email(),
            name,
            amount,
            currency,
            term,
            return_way,
            security,
            percentage,
            form,
            commentary
        )

    @staticmethod
    def add_lot_to_favorites(lot_id):
        database = DatabaseHandler()
        database.add_lot_to_favorites(User.email(), lot_id)

    @staticmethod
    def remove_lot_from_favorites(lot_id):
        database = DatabaseHandler()
        database.remove_lot_from_favorites(User.email(), lot_id)

    @staticmethod
    def add_avatar(image):
        database = DatabaseHandler()
        database.set_user_avatar(User.email(), image)

    @staticmethod
    def get_avatar_link():
        database = DatabaseHandler()
        return database.get_user_avatar_link(User.email())

    @staticmethod
    def delete_avatar():
        database = DatabaseHandler()
        database.delete_user_avatar(User.email())

    @staticmethod
    def subscribe_to_lot(lot_id: int, type: str, message: str) -> bool:
        database = DatabaseHandler()
        return database.subscribe_user_to_lot(User.email(), lot_id, SubscriptionTypes[type], message)

    @staticmethod
    def unsubscribe_from_lot(lot_id):
        database = DatabaseHandler()
        database.unsubscribe_user_from_lot(User.email(), lot_id)

    @staticmethod
    def get_subscriptions():
        database = DatabaseHandler()
        return database.get_user_subscriptions(User.email())


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

    def verify_email_from_code(self, code):
        database = DatabaseHandler()
        try:
            database.verify_email_confirmation(code)
        except EmailValidationError:
            raise
        else:
            return jsonify({'msg': 'Email was succesfully confirmed.'})
        finally:
            try:
                database.delete_email_confirmation_code(code)
            except sqlite3.Error:
                pass

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

    def create(self, email, password):
        database = DatabaseHandler()
        database.create_user(email, password)