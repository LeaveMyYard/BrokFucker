from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatabaseHandler
from flask import Flask, abort, jsonify, request, make_response
import lib.util.exceptions as APIExceptions
from lib.user import User

class Moderator:
    auth = HTTPBasicAuth()
    login_required = auth.login_required
    email = auth.username

    @staticmethod
    @auth.verify_password
    def verify_password(email, password):
        database = DatabaseHandler()
        return database.check_password(email, password) and database.is_moderator(email)

    @staticmethod
    @auth.error_handler
    def unauthorized():
        return make_response(jsonify({'code': -1002, 'msg': 'You are not authorized to execute this request.'}), 403)

    @staticmethod
    def add(email):
        database = DatabaseHandler()

        if not database.check_user_exists(email):
            raise APIExceptions.UserNotExists(email)

        if database.is_administrator(email):
            raise APIExceptions.ModeratorAddingError(f'Administrator is also a moderator.')

        if database.is_moderator(email):
            raise APIExceptions.ModeratorAddingError(f'User {email} is already a moderator.')
        
        database.set_moderator_rights(email)

    @staticmethod
    def remove(email):
        database = DatabaseHandler()

        if not database.check_user_exists(email):
            raise APIExceptions.UserNotExists(email)

        if database.is_administrator(email):
            raise APIExceptions.ModeratorAddingError(f'Could not remove rights from administrator.')

        if not database.is_moderator(email):
            raise APIExceptions.ModeratorAddingError(f'User {email} is not a moderator.')
        
        database.remove_moderator_rights(email)