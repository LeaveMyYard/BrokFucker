from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatadaseHandler
from flask import Flask, abort, jsonify, request, make_response

class User():
    auth = HTTPBasicAuth()
    login_required = auth.login_required

    @staticmethod
    @auth.verify_password
    def verify_password(email, password):
        database = DatadaseHandler()
        return database.check_password(email, password) 

    @staticmethod
    @auth.error_handler
    def unauthorized():
        return make_response(jsonify({'code': -1002, 'msg': 'You are not authorized to execute this request.'}), 403)