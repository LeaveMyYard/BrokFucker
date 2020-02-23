from flask import Flask, abort, jsonify, request, make_response, send_from_directory, send_file
from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatabaseHandler
from lib.user import User as user
from lib.moderator import Moderator as moderator
from lib.lot import Lot
from lib.util.exceptions import IndexedException
from datetime import timedelta

app = Flask(__name__)

class WebApp:
    @staticmethod
    @app.route('/')
    def root():
        return send_file('src/index.html')

    @staticmethod
    @app.route('/<path:path>')
    def send_web(path):
        if not path.endswith('.html'):
            return send_from_directory('src', path + '.html')
        return send_from_directory('src', path)

class RestAPI:
    # Initialize database
    DatabaseHandler.init_tables()
    DatabaseHandler.run_verification_code_clearer(
        timedelta(hours=12),
        timedelta(days=7)
    )

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
        IndexedException:
            lambda error: make_response(jsonify({'code': error.error_id, 'msg': error.args[0]}), 409)
    }

    # Then, looping through all that dictionary we will call a decorator
    # as a normal function, creating all the error handlers
    for ex in exceptions_dict:
        app.errorhandler(ex)(
            exceptions_dict[ex]
        )

    @staticmethod
    def message(msg) -> str:
        return jsonify(
            {
                'msg': msg
            }
        )

    @staticmethod
    @route('ping', methods=['GET'])
    def ping():
        return RestAPI.message('pong'), 200

    @staticmethod
    @route('getUserData', methods=['GET'])
    @user.login_required
    def check_user():
        return jsonify(user().get_data()), 200

    @staticmethod
    @route('register', methods=['POST'])
    def register():
        if not request.json:
            abort(400)

        data_required = [
            'email',
            'password',
        ]

        for data in data_required:
            if data not in request.json:
                abort(400)

        user.begin_email_verification(
            request.json['email'],
            request.json['password'],
        )

        return RestAPI.message(f"Verification is sent to {request.json['email']}"), 201

    @staticmethod
    @route('register/verify/<string:verification_hash>')
    def confirm_verification(verification_hash):
        return user.verify_email_from_code(verification_hash), 201

    @staticmethod
    @route('lots/createNew', methods=['POST'])
    @user.login_required
    def create_lot():
        if not request.json:
            abort(400)
        
        data_required = [
            'name',
            'amount',
            'currency',
            'term',
            'return_way',
            'security',
            'percentage',
            'form',
        ]

        for data in data_required:
            if data not in request.json:
                abort(400)

        user.create_lot(*[request.json[data] for data in data_required])

        return RestAPI.message('New lot created'), 201

    @staticmethod
    @route('lots/<int:lot_id>/approve', methods=['PUT'])
    @moderator.login_required
    def approve_lot(lot_id):
        Lot.approve(lot_id)
        return RestAPI.message('A lot is now approved'), 201

    @staticmethod
    @route('lots/<int:lot_id>/setSecurityChecked', methods=['PUT'])
    @moderator.login_required
    def set_security_checked(lot_id):
        Lot.set_security_checked(lot_id, True)
        return RestAPI.message('Lot\'s security is now checked'), 201

    @staticmethod
    @route('lots/<int:lot_id>/setSecurityUnchecked', methods=['PUT'])
    @moderator.login_required
    def set_security_unchecked(lot_id):
        Lot.set_security_checked(lot_id, False)
        return RestAPI.message('Lot\'s security is no more checked'), 201

    @staticmethod
    @route('lots/approved', methods=['GET'])
    @user.login_required
    def get_approved_lots():
        return jsonify(Lot.get_all_approved_lots()), 200

    @staticmethod
    @route('lots/unapproved', methods=['GET'])
    @moderator.login_required
    def get_unapproved_lots():
        return jsonify(Lot.get_all_unapproved_lots()), 200

    @staticmethod
    @route('lots/favorites/<int:lot_id>', methods=['POST', 'PUT', 'DELETE'])
    @user.login_required
    def updateFavoriteLots(lot_id):
        if request.method == 'POST' or request.method == 'PUT':
            user.add_lot_to_favorites(lot_id)
            return RestAPI.message('A lot is added to favorites'), 201
        if request.method == 'DELETE':
            user.remove_lot_from_favorites(lot_id)
            return RestAPI.message('A lot is removed from favorites'), 201

    @staticmethod
    @route('lots/favorites', methods=['GET'])
    @user.login_required
    def getFavoriteLots():
        return jsonify(user.get_favorites()), 200

if __name__ == '__main__':
    app.run(debug=True)