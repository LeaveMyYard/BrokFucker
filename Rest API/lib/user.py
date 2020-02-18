from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatadaseHandler
from flask import Flask, abort, jsonify, request, make_response

class User:
    auth = HTTPBasicAuth()
    login_required = auth.login_required
    email = auth.username

    @staticmethod
    @auth.verify_password
    def verify_password(email, password):
        database = DatadaseHandler()
        return database.check_password(email, password)

    @staticmethod
    @auth.error_handler
    def unauthorized():
        return make_response(jsonify({'code': -1002, 'msg': 'You are not authorized to execute this request.'}), 403)

    @staticmethod
    def create(email, password):
        database = DatadaseHandler()
        database.create_user(email, password)

    @staticmethod
    def get_data():
        database = DatadaseHandler()
        return database.get_user_data(User.email())

    @staticmethod
    def create_lot(
        name,
        amount,
        currency,
        term,
        return_way,
        security,
        percentage,
        form
    ):
        database = DatadaseHandler()
        database.create_new_lot(
            User.email(),
            name,
            amount,
            currency,
            term,
            return_way,
            security,
            percentage,
            form
        )

    @staticmethod
    def add_lot_to_favorites(lot_id):
        database = DatadaseHandler()
        database.add_lot_to_favorites(User.email(), lot_id)

    @staticmethod
    def remove_lot_from_favorites(lot_id):
        database = DatadaseHandler()
        database.remove_lot_from_favorites(User.email(), lot_id)

    @staticmethod
    def get_favorites():
        database = DatadaseHandler()
        return database.get_favorites(User.email())