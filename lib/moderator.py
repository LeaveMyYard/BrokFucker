from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatabaseHandler
from flask import Flask, abort, jsonify, request, make_response


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
        return make_response(
            jsonify(
                {
                    "code": -1002,
                    "msg": "You are not authorized to execute this request.",
                }
            ),
            403,
        )
