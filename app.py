from flask import Flask, abort, jsonify, request, make_response, send_from_directory, send_file
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatabaseHandler
from lib.user import User as user
from lib.moderator import Moderator as moderator
from lib.lot import Lot
from lib.settings import Settings
from lib.util.exceptions import IndexedException
from datetime import timedelta
from typing import Union, Dict, Callable

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'data/images/upload'
app.config['MAX_CONTENT_PATH'] = Settings.get_maximum_image_size()

class WebApp:
    # This one redirects main page to index.html
    @staticmethod
    @app.route('/')
    def root():
        return send_file('src/index.html')

    # Here all the data for WebApp is redirected to src folder.
    # So, the actual web pages should be in that folder
    @staticmethod
    @app.route('/<path:path>')
    def send_web(path):
        if '.' not in path:
            return send_from_directory('src', path + '.html')
        return send_from_directory('src', path)

    # Also redirect all /image requests to data/images
    @staticmethod
    @app.route('/image/<path:path>')
    def send_image(path):
        return send_from_directory('data/images', path)

    # Simplify the exceptions handlers.
    # Rather than definging a function for each error or code by hands we will
    # store all the possible ints and Exceptions as keys and
    # corresponding lambda functions as values.

    exceptions_responses = {
        404: lambda error: send_file('src/404.html')
    }

class RestAPI:

    # -------------------------------------------------------------------------
    # Private stuff
    # -------------------------------------------------------------------------

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
    exceptions_responses = {
        400: lambda error: {'code': -1000, 'msg': 'An unknown error occured while processing the request.'},
        404: lambda error: {'code': -1001, 'msg': 'The stuff you requested for is not found.'},
        IndexedException: lambda error: {'code': error.error_id, 'msg': error.args[0]},
    }

    @staticmethod
    def message(msg) -> str:
        return jsonify(
            {
                'msg': msg
            }
        )

    # -------------------------------------------------------------------------
    # Public stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('ping', methods=['GET'])
    def ping():
        return RestAPI.message('pong'), 200

    # -------------------------------------------------------------------------
    # Registration stuff
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # User stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('user', methods=['GET'])
    @user.login_required
    def check_user():
        return jsonify(user.get_data()), 200

    @staticmethod
    @route('user/avatar', methods=['GET', 'POST', 'DELETE'])
    @user.login_required
    def edit_avatar():
        if request.method == 'GET':
            user.get_avatar_link()
            return jsonify({'link': user.get_avatar_link()}), 200
        if request.method == 'POST':
            user.add_avatar(request.files['file'])
            return RestAPI.message('New avatar is saved'), 201
        if request.method == 'DELETE':
            user.delete_avatar()
            return RestAPI.message('Your avatar is now deleted'), 201

    # -------------------------------------------------------------------------
    # Lots stuff
    # -------------------------------------------------------------------------

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
            'commentary'
        ]

        for data in data_required:
            if data not in request.json:
                abort(400)

        user.create_lot(*[request.json[data] for data in data_required])

        return RestAPI.message('New lot created'), 201

    @staticmethod
    @route('lots/approved', methods=['GET'])
    @route('lots', methods=['GET'])
    def get_approved_lots():
        return jsonify(Lot.get_all_approved_lots()), 200

    @staticmethod
    @route('lots/favorites/<int:lot_id>', methods=['PUT', 'DELETE'])
    @user.login_required
    def update_favorite_lots(lot_id):
        if request.method == 'PUT':
            user.add_lot_to_favorites(lot_id)
            return RestAPI.message('A lot is added to favorites'), 201
        if request.method == 'DELETE':
            user.remove_lot_from_favorites(lot_id)
            return RestAPI.message('A lot is removed from favorites'), 201

    @staticmethod
    @route('lots/favorites', methods=['GET'])
    @user.login_required
    def get_favorite_lots():
        return jsonify(user.get_favorites()), 200

    @staticmethod
    @route('lots/personal', methods=['GET'])
    @user.login_required
    def get_personal_lots():
        return jsonify(user.get_personal()), 200

    # -------------------------------------------------------------------------
    # Moderator stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('lots/<int:lot_id>/approve', methods=['PUT'])
    @moderator.login_required
    def approve_lot(lot_id):
        Lot.approve(lot_id)
        return RestAPI.message('A lot is now approved'), 201

    @staticmethod
    @route('lots/<int:lot_id>/security', methods=['PUT', 'DELETE'])
    @moderator.login_required
    def set_security_checked(lot_id):
        if request.type == 'PUT':
            Lot.set_security_checked(lot_id, True)
            return RestAPI.message('Lot\'s security is now checked'), 201
        if request.type == 'DELETE':
            Lot.set_security_checked(lot_id, False)
            return RestAPI.message('Lot\'s security is no more checked'), 201

    @staticmethod
    @route('lots/unapproved', methods=['GET'])
    @moderator.login_required
    def get_unapproved_lots():
        return jsonify(Lot.get_all_unapproved_lots()), 200

    # -------------------------------------------------------------------------
    # Admin stuff
    # -------------------------------------------------------------------------


class Server:
    # This function processes exceptions.
    # If the request is for api, will respond as it is an api responce
    # Otherwise, will respond as a Web App 
    @staticmethod
    def process_exception(ex):
        if not request.path.startswith('/api/') and ex in WebApp.exceptions_responses:
            return WebApp.exceptions_responses[ex](ex)
        elif ex in RestAPI.exceptions_responses:
            return make_response(jsonify(RestAPI.exceptions_responses[ex](ex)), ex if isinstance(ex, int) else 403)
            

    # Then, looping through all that exceptions from WebApp and RestAPI
    # Creates functions with corresponding flask decorator to process
    # an error for that case
    exceptions = set(WebApp.exceptions_responses) & set(RestAPI.exceptions_responses)

    # This one is just to prevent errors appearing in VSCode
    # Actually there is no error, just IDE being buged
    ex = None
    
    for ex in exceptions:
        @staticmethod
        @app.errorhandler(ex)
        def error_handler(error, exception = ex):
            return Server.process_exception(exception)

if __name__ == '__main__':
    app.run(debug=True)