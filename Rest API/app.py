from flask import Flask, abort, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatadaseHandler
from lib.user import User as user
from lib.moderator import Moderator as moderator
from lib.util.exceptions import RegistrationError

app = Flask(__name__)

class RestServer:

    # Creating our own route decorator. 
    # It will be almost the same as app.route except it will always be on '/api/v1/'
    route = lambda loc, **options: app.route('/api/v1/' + loc, **options)

    # Simplify the exceptions handlers.
    # Rather than definging a function for each error or code by hands we will
    # store all the possible ints and Exceptions as keys and
    # corresponding lambda functions as values.
    exceptions_dict = {
        400: 
            lambda error: make_response(jsonify({'code': -1000, 'msg': 'An unknown error occured while processing the request.'}), 400),
        404: 
            lambda error: make_response(jsonify({'code': -1001, 'msg': 'The stuff you requested for is not found.'}), 404),
        RegistrationError:
            lambda error: make_response(jsonify({'code': error.error_id, 'msg': error.args[0]}), 409)
    }

    # Then, looping through all that dictionary we will call decorator
    # as a normal function, creating all the functions
    for ex in exceptions_dict:
        app.errorhandler(ex)(
            exceptions_dict[ex]
        )

    @staticmethod
    @route('ping', methods=['GET'])
    def ping():
        return jsonify({}), 200

    @staticmethod
    @route('testUser', methods=['GET'])
    @user.login_required
    def check_user():
        return jsonify({'msg': 'Successful'}), 200

    @staticmethod
    @route('testModerator', methods=['GET'])
    @moderator.login_required
    def check_mod():
        return jsonify({'msg': 'Successful'}), 200

    @staticmethod
    @route('register', methods=['POST'])
    def register():
        if not request.json or not 'email' in request.json or not 'password' in request.json:
            abort(400)

        email = request.json['email']
        password = request.json['password']

        database = DatadaseHandler()
        database.create_user(email, password)

        return jsonify({'msg': 'New user created'}), 201

if __name__ == '__main__':
    app.run(debug=True)