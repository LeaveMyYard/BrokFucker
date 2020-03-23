from flask import Flask, abort, jsonify, request, make_response, send_from_directory, send_file
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatabaseHandler
from lib.user import User as user
from lib.moderator import Moderator as moderator
from lib.admin import Admin as administrator
from lib.lot import Lot
from lib.settings import Settings
from datetime import timedelta
from typing import Union, Dict, Callable, List
import json
import lib.util.exceptions as APIExceptions
import re

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
    @app.route('/image/lot/<path:path>')
    def send_lot_image(path):
        return send_from_directory('data/images/lots', path)

    @staticmethod
    @app.route('/image/user/<path:path>')
    def send_user_image(path):
        return send_from_directory('data/images/user', path)

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
        APIExceptions.IndexedException: lambda error: {'code': error.error_id, 'msg': error.args[0]},
    }

    @staticmethod
    def message(msg) -> str:
        return jsonify(
            {
                'msg': msg
            }
        )

    @staticmethod
    def request_data_to_json(request) -> dict:
        try:
            return json.loads(request)
        except json.decoder.JSONDecodeError:
            raise APIExceptions.NoJsonError()

    @staticmethod
    def check_required_fields(json, data_required: List[str]) -> None:
        for data in data_required:
            if data not in json:
                raise APIExceptions.NotEnoughDataError(data_required, json.keys())

    @staticmethod
    def check_fields_values(json: Dict, field_setting: str) -> None:
        settings = Settings.get_enter_settings()[field_setting]
        for key, value in json.items():
            if settings[key] is None:
                continue
            elif isinstance(settings[key], str):
                if not re.fullmatch(settings[key], value):
                    raise APIExceptions.JSONValueException(key, settings[key], value)
            elif isinstance(settings[key], list):
                if value not in settings[key]:
                    raise APIExceptions.JSONValueException(key, settings[key], value)

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
            raise APIExceptions.NoJsonError()

        data_required = [
            'email',
            'password',
        ]

        for data in data_required:
            if data not in request.json:
                raise APIExceptions.NotEnoughDataError(data_required, request.json.keys())

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
    @route('user', methods=['PUT'])
    @user.login_required
    def edit_user_data():
        try:
            request_json = json.loads(request.data)
        except json.decoder.JSONDecodeError:
            raise APIExceptions.NoJsonError()

        data_required = {
            'phone': 'phone_number',
            'name': 'name',
        }

        for data in data_required:
            if data in request_json:
                user.edit_data(data_required[data], request_json[data])

        return RestAPI.message('Data is edited successful'), 201

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
    @route('lots/settings', methods=['GET'])
    def get_lot_settings():
        return jsonify(Lot.get_settings()), 200

    @staticmethod
    @route('lots', methods=['POST'])
    @user.login_required
    def create_lot():
        request_json = RestAPI.request_data_to_json(request.data)

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

        RestAPI.check_required_fields(request_json, data_required)
        RestAPI.check_fields_values(request_json, "lot")

        return jsonify({'lot_id': user.create_lot(*[request_json[data] for data in data_required]) }), 201

    @staticmethod
    @route('lots/approved', methods=['GET'])
    @route('lots', methods=['GET'])
    def get_approved_lots():
        return jsonify(Lot.get_all_approved_lots()), 200

    @staticmethod
    @route('lots/<int:lot_id>', methods=['GET'])
    def get_lot(lot_id):
        return jsonify(Lot.get_lot(lot_id)), 200

    @staticmethod
    @route('lots/<int:lot_id>', methods=['PUT'])
    @user.login_required
    def update_lot(lot_id):
        if not Lot.can_user_edit(user.email(), lot_id):
            raise APIExceptions.NoPermissionError()

        if not request.json:
            raise APIExceptions.NoJsonError()

        data_available = [
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

        RestAPI.check_fields_values(request.json, "lot")

        for data in data_available:
            if data in request.json:
                Lot.update_data(lot_id, data, request.json[data])

        return RestAPI.message('A lot is changed'), 201

    @staticmethod
    @route('lots/<int:lot_id>', methods=['DELETE'])
    @user.login_required
    def delete_lot(lot_id):
        if not Lot.can_user_edit(user.email(), lot_id):
            raise APIExceptions.NoPermissionError()
        
        Lot.delete_lot(lot_id)
        return RestAPI.message('A lot is deleted'), 201

    @staticmethod
    @route('lots/<int:lot_id>', methods=['POST'])
    @user.login_required
    def restore_lot(lot_id):
        if not Lot.can_user_edit(user.email(), lot_id):
            raise APIExceptions.NoPermissionError()

        Lot.restore_lot(lot_id)
        return RestAPI.message('A lot is restored'), 201

    @staticmethod
    @route('lots/<int:lot_id>/photos', methods=['GET'])
    def get_lot_photo(lot_id):
        return jsonify({'link': Lot.get_photos(lot_id)}), 200

    @staticmethod
    @route('lots/<int:lot_id>/photos', methods=['POST'])
    @user.login_required
    def add_lot_photo(lot_id):
        if not Lot.can_user_edit(user.email(), lot_id):
            raise APIExceptions.NoPermissionError()
        
        a = request.files
        resp = {filename: Lot.add_photo(request.files[filename], lot_id) for filename in request.files}

        return jsonify(resp), 201

    @staticmethod
    @route('lots/<int:lot_id>/photos/<int:photo_id>', methods=['DELETE'])
    @user.login_required
    def remove_lot_photo(lot_id, photo_id):
        if not Lot.can_user_edit(user.email(), lot_id):
            raise APIExceptions.NoPermissionError()
        
        return jsonify(Lot.remove_photo(lot_id, photo_id)), 201

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

    @staticmethod
    @route('lots/personal/deleted', methods=['GET'])
    @user.login_required
    def get_personal_deleted_lots():
        return jsonify(user.get_personal_deleted()), 200

    @staticmethod
    @route('lots/subscription/<int:lot_id>', methods=['PUT'])
    @user.login_required
    def subscribe_to_lot(lot_id):
        request_json = RestAPI.request_data_to_json(request.data)

        data_required = [
            'type',
            'message',
        ]

        RestAPI.check_required_fields(request_json, data_required)

        if user.subscribe_to_lot(lot_id, *[request_json[data] for data in data_required]):
            return RestAPI.message(f'You are now subscribed to lot {lot_id}'), 201
        else:
            return RestAPI.message('You are already subscribed'), 200
            

    @staticmethod
    @route('lots/subscription/<int:lot_id>', methods=['DELETE'])
    @user.login_required
    def unsubscribe_from_lot(lot_id):
        try:
            user.unsubscribe_from_lot(lot_id)
            return RestAPI.message(f'You are no longer subscribed to lot {lot_id}'), 201
        except:
            return RestAPI.message('You are not subscribed'), 200

    @staticmethod
    @route('lots/subscription', methods=['GET'])
    @user.login_required
    def get_subscribed_lots():
        return jsonify({'lots': user.get_subscriptions()}), 200

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

    @staticmethod
    @route('lots/subscription/approved', methods=['GET'])
    @moderator.login_required
    def get_approved_subscriptions():
        return jsonify({'lots': Lot.get_approved_subscriptions()}), 200

    @staticmethod
    @route('lots/subscription/unapproved', methods=['GET'])
    @moderator.login_required
    def get_unapproved_subscriptions():
        return jsonify({'lots': Lot.get_unapproved_subscriptions()}), 200

    # -------------------------------------------------------------------------
    # Admin stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('user/<string:email>/moderator', methods=['PUT', 'POST'])
    @administrator.login_required
    def give_moderator_rights(email):
        moderator.add(email)
        return RestAPI.message(f'{email} is now a moderator.')

    @staticmethod
    @route('user/<string:email>/moderator', methods=['DELETE'])
    @administrator.login_required
    def remove_moderator_rights(email):
        moderator.remove(email)
        return RestAPI.message(f'{email} is no longer a moderator.')

class Server:
    # This function processes exceptions.
    # If the request is for api, will respond as it is an api responce
    # Otherwise, will respond as a Web App 
    @staticmethod
    def process_exception(ex, error):
        if not request.path.startswith('/api/') and ex in WebApp.exceptions_responses:
            return WebApp.exceptions_responses[ex](error), ex if isinstance(ex, int) else 403
        elif ex in RestAPI.exceptions_responses:
            return make_response(jsonify(RestAPI.exceptions_responses[ex](error)), ex if isinstance(ex, int) else 403)
            

    # Then, looping through all that exceptions from WebApp and RestAPI
    # Creates functions with corresponding flask decorator to process
    # an error for that case
    exceptions = set(WebApp.exceptions_responses) | set(RestAPI.exceptions_responses)

    # This one is just to prevent errors appearing in VSCode
    # Actually there is no error, just IDE being buged
    ex = None
    
    for ex in exceptions:
        @staticmethod
        @app.errorhandler(ex)
        def error_handler(error, exception = ex):
            return Server.process_exception(exception, error)

if __name__ == '__main__':
    app.run(debug=True)