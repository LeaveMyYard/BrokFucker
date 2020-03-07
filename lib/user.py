from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatabaseHandler
from flask import Flask, abort, jsonify, request, make_response
from lib.util.exceptions import EmailValidationError
from lib.util.hash import sha256
from lib.settings import Settings
from werkzeug.utils import secure_filename
from PIL import Image
from os import path, remove

class User:
    auth = HTTPBasicAuth()
    login_required = auth.login_required
    email = auth.username

    @staticmethod
    @auth.verify_password
    def verify_password(email, password):
        database = DatabaseHandler()
        return database.check_password(email, password)

    @staticmethod
    @auth.error_handler
    def unauthorized():
        return make_response(jsonify({'code': -1002, 'msg': 'You are not authorized to execute this request.'}), 403)

    @staticmethod
    def begin_email_verification(email, password):
        database = DatabaseHandler()
        database.create_email_confirmation_request(email, password)

    @staticmethod
    def verify_email_from_code(code):
        database = DatabaseHandler()
        try:
            link = database.verify_email_confirmation(code)
        except EmailValidationError as e:
            database.delete_email_confirmation_code(code)
            if e.link is None: 
                raise
            else:
                return f'<head><meta http-equiv="refresh" content="1;URL={request.host_url}{e.link}?msg={e.args[0].replace(" ", "_")}" /></head>'

        database.delete_email_confirmation_code(code)
        if link is None:
            return jsonify({'msg': 'Email was succesfully confirmed.'})
        else:
            return f'<head><meta http-equiv="refresh" content="1;URL={request.host_url}{link}" /></head>'

    @staticmethod
    def create(email, password):
        database = DatabaseHandler()
        database.create_user(email, password)

    @staticmethod
    def get_data():
        database = DatabaseHandler()
        res = database.get_user_data(User.email())
        res['avatar'] = User.get_avatar_link()
        return res

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
        database.create_new_lot(
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
    def get_favorites():
        database = DatabaseHandler()
        return database.get_favorites(User.email())

    @staticmethod
    def get_personal():
        database = DatabaseHandler()
        return database.get_personal(User.email())

    @staticmethod
    def get_personal_deleted():
        database = DatabaseHandler()
        return database.get_personal_deleted(User.email())

    @staticmethod
    def add_avatar(image):
        temporary_file_location = f'data/images/temp/{secure_filename(image.filename)}'
        image.save(temporary_file_location)

        im = Image.open(temporary_file_location)
        file_location = f'data/images/user/{sha256(User.email())}.jpg'
        im = im.convert("RGB")
        im.save(file_location)

        remove(temporary_file_location)

    @staticmethod
    def get_avatar_link():
        file_location = f'data/images/user/{sha256(User.email())}.jpg'
        try:
            f = open(file_location)
            return f'{request.host_url}image/user/{sha256(User.email())}.jpg'
        except:
            return f'{request.host_url}image/user/default.jpg'

    @staticmethod
    def delete_avatar():
        file_location = f'data/images/user/{sha256(User.email())}.jpg'
        remove(file_location)

    @staticmethod
    def subscribe_to_lot(lot_id):
        database = DatabaseHandler()
        database.subscribe_user_to_lot(User.email(), lot_id)

    @staticmethod
    def unsubscribe_from_lot(lot_id):
        database = DatabaseHandler()
        database.unsubscribe_user_from_lot(User.email(), lot_id)

    @staticmethod
    def get_subscriptions():
        database = DatabaseHandler()
        return database.get_user_subscriptions(User.email())