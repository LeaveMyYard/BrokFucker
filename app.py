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
import copy

from lib.util.logger import init_logger

from datetime import datetime, timedelta
from threading import Timer

app = Flask(__name__)
CORS(app)

logger = init_logger(__name__)

app.config['UPLOAD_FOLDER'] = 'data/images/upload'
app.config['MAX_CONTENT_PATH'] = Settings.get_maximum_image_size()

ip_weights = {
    '1s': {},
    '1m': {},
    '1h': {}
}

ban_list = {}

max_weights = Settings.get_max_weights()

def remove_1s():
    ip_weights['1s'] = {}
    t = Timer(1.0, remove_1s)
    t.start()

def remove_1m():
    ip_weights['1m'] = {}
    t = Timer(60.0, remove_1m)
    t.start()

def remove_1h():
    ip_weights['1h'] = {}
    t = Timer(3600.0, remove_1h)
    t.start()

remove_1s()
remove_1m()
remove_1h()

def weighted(weight):
    def decorator(func):
        def res_func(*args, **kwargs):
            request_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

            logger.debug(f"Request from {request_ip} with weight {weight}.")

            if request_ip in ban_list:
                duration = ban_list[request_ip][0] - datetime.now()
                if duration < timedelta(seconds=0):
                    ban_list.pop(request_ip)
                else:
                    raise APIExceptions.MaximumRequestsTimeout(time_to_end=int((ban_list[request_ip][0] - datetime.now()).total_seconds()))

            ban_durations = [timedelta(minutes=5), timedelta(minutes=15), timedelta(hours=1), timedelta(days=1)]
            
            for key, values in ip_weights.items():
                if request_ip not in values:
                    values[request_ip] = 0
                if values[request_ip] > max_weights[key]:
                    ban_list[request_ip] = [..., (ban_list[request_ip][1] if request_ip in ban_list else []) + [datetime.now()]]
                    ban_list[request_ip][1] = ban_cases = list(filter(lambda time: time > datetime.now() - timedelta(days=1), ban_list[request_ip][1]))

                    for stats in ip_weights:
                        stats[request_ip] = 0

                    ban_time = ban_durations[len(ban_cases) - 1]
                    ban_list[request_ip][0] = datetime.now() + ban_time

                    logger.warning(f"User {request_ip} was banned for {ban_time}")
                    raise APIExceptions.MaximumRequestsTimeout(int(ban_time.total_seconds()))
                values[request_ip] += weight

            logger.debug(f"Stats: (1s: {ip_weights['1s'][request_ip]}, 1m: {ip_weights['1m'][request_ip]}, 1h: {ip_weights['1h'][request_ip]})")

            return func(*args, *kwargs)

        res_func.__name__ = func.__name__

        return res_func
    return decorator


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
        APIExceptions.IndexedException: lambda error: {'code': error.error_id, 'msg': error.args[0], 'type': error.__class__.__name__},
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
            if key not in settings:
                pass
            elif settings[key] is None:
                pass
            else:
                RestAPI.validate_field(key, value, settings[key])

    @staticmethod
    def validate_field(field_name, field_value, validation):
        if isinstance(validation, str):
            if not re.fullmatch(validation, field_value):
                raise APIExceptions.JSONValueException(field_name, validation, field_value)
        elif isinstance(validation, list):
            if field_value not in validation:
                raise APIExceptions.JSONValueException(field_name, validation, field_value)

    # -------------------------------------------------------------------------
    # Public stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('ping', methods=['GET'])
    @weighted(weight=1)
    def ping():
        return RestAPI.message('pong'), 200

    # -------------------------------------------------------------------------
    # Registration stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('register', methods=['POST'])
    @weighted(weight=10)
    def register():
        request_json = RestAPI.request_data_to_json(request.data)

        data_required = [
            'email',
            'password',
        ]

        for data in data_required:
            if data not in request_json:
                raise APIExceptions.NotEnoughDataError(data_required, request_json.keys())

        RestAPI.check_fields_values(request_json, "register")

        user.begin_email_verification(
            request_json['email'],
            request_json['password'],
        )

        return RestAPI.message(f"Verification is sent to {request_json['email']}"), 201

    @staticmethod
    @route('register/verify/<string:verification_hash>')
    @weighted(weight=2)
    def confirm_verification(verification_hash):
        return user.verify_email_from_code(verification_hash), 201

    # -------------------------------------------------------------------------
    # User stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('user', methods=['GET'])
    @user.login_required
    @weighted(weight=1)
    def check_user():
        return jsonify(user.get_data()), 200

    @staticmethod
    @route('user/password', methods=['PUT'])
    @user.login_required
    @weighted(weight=10)
    def change_password():
        request_json = RestAPI.request_data_to_json(request.data)

        data_required = [
            'password'
        ]

        RestAPI.check_required_fields(request_json, data_required)
        RestAPI.check_fields_values(request_json, "register")

        user.change_password(request_json['password'])
        return RestAPI.message(f'Verification in sent to {user.email()}')

    @staticmethod
    @route('user/password/verify/<string:code>')
    @weighted(weight=2)
    def verify_password_code(code):
        user.verify_password_change(code)
        return RestAPI.message(f'Password was successfuly changed.')

    @staticmethod
    @route('user/restore/<string:email>')
    @weighted(weight=10)
    def restore_account(email):
        user.restore_account(email)
        return RestAPI.message(f'Verification in sent to {email}')

    @staticmethod
    @route('user/restore/verify/<string:code>')
    @weighted(weight=2)
    def verify_account_restore(code):
        user.verify_account_restore(code)
        return RestAPI.message(f'Temporary password is sent to your email.')

    @staticmethod
    @route('user', methods=['PUT'])
    @user.login_required
    @weighted(weight=2)
    def edit_user_data():
        request_json = RestAPI.request_data_to_json(request.data)

        data_required = {
            'phone': 'phone_number',
            'name': 'name',
        }

        RestAPI.check_fields_values(request_json, "user_data")

        for data in data_required:
            if data in request_json:
                user.edit_data(data_required[data], request_json[data])

        return RestAPI.message('Data is edited successful'), 201

    @staticmethod
    @route('user/avatar', methods=['GET', 'POST', 'DELETE'])
    @user.login_required
    @weighted(weight=2)
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
    @weighted(weight=1)
    def get_lot_settings():
        return jsonify(Lot.get_settings()), 200

    @staticmethod
    @route('lots', methods=['POST'])
    @user.login_required
    @weighted(weight=1)
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
    @route('lots/approved', methods=['GET', 'POST'])
    @route('lots', methods=['GET'])
    @weighted(weight=5)
    def get_approved_lots():
        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(Lot.get_all_approved_lots(lot_filter)), 200

    @staticmethod
    @route('lots/<int:lot_id>', methods=['GET'])
    @weighted(weight=1)
    def get_lot(lot_id):
        return jsonify(Lot(lot_id).get_lot_data()), 200

    @staticmethod
    @route('lots/<int:lot_id>', methods=['PUT'])
    @user.login_required
    @weighted(weight=3)
    def update_lot(lot_id):
        lot = Lot(lot_id)
        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()

        request_json = RestAPI.request_data_to_json(request.data)

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

        RestAPI.check_fields_values(request_json, "lot")

        for data in data_available:
            if data in request_json:
                lot.update_data(data, request_json[data])

        return RestAPI.message('A lot is changed'), 201

    @staticmethod
    @route('lots/<int:lot_id>', methods=['DELETE'])
    @user.login_required
    @weighted(weight=2)
    def delete_lot(lot_id):
        lot = Lot(lot_id)
        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()
        
        lot.delete_lot()
        return RestAPI.message('A lot is deleted'), 201

    @staticmethod
    @route('lots/<int:lot_id>', methods=['POST'])
    @user.login_required
    @weighted(weight=2)
    def restore_lot(lot_id):
        lot = Lot(lot_id)
        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()

        lot.restore_lot()
        return RestAPI.message('A lot is restored'), 201

    @staticmethod
    @route('lots/<int:lot_id>/photos', methods=['GET'])
    @weighted(weight=2)
    def get_lot_photo(lot_id):
        return jsonify({'link': Lot(lot_id).get_photos()}), 200

    @staticmethod
    @route('lots/<int:lot_id>/photos', methods=['POST'])
    @user.login_required
    @weighted(weight=3)
    def add_lot_photo(lot_id):
        lot = Lot(lot_id)
        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()
        
        resp = {filename: lot.add_photo(request.files[filename]) for filename in request.files}

        return jsonify(resp), 201

    @staticmethod
    @route('lots/<int:lot_id>/photos/<int:photo_id>', methods=['DELETE'])
    @user.login_required
    @weighted(weight=2)
    def remove_lot_photo(lot_id, photo_id):
        lot = Lot(lot_id)

        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()
        
        return jsonify(lot.remove_photo(photo_id)), 201

    @staticmethod
    @route('lots/favorites/<int:lot_id>', methods=['PUT', 'DELETE'])
    @user.login_required
    @weighted(weight=1)
    def update_favorite_lots(lot_id):
        if request.method == 'PUT':
            user.add_lot_to_favorites(lot_id)
            return RestAPI.message('A lot is added to favorites'), 201
        if request.method == 'DELETE':
            user.remove_lot_from_favorites(lot_id)
            return RestAPI.message('A lot is removed from favorites'), 201

    @staticmethod
    @route('lots/favorites', methods=['GET', 'POST'])
    @user.login_required
    @weighted(weight=3)
    def get_favorite_lots():
        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(Lot.get_favorites(user.email(), lot_filter)), 200

    @staticmethod
    @route('lots/personal', methods=['GET', 'POST'])
    @user.login_required
    @weighted(weight=3)
    def get_personal_lots():
        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(Lot.get_personal(user.email(), lot_filter)), 200

    @staticmethod
    @route('lots/personal/deleted', methods=['GET', 'POST'])
    @user.login_required
    @weighted(weight=3)
    def get_personal_deleted_lots():
        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(Lot.get_personal_deleted(user.email(), lot_filter)), 200

    @staticmethod
    @route('lots/personal/deleted/<int:lot_id>', methods=['DELETE'])
    @user.login_required
    @weighted(weight=1)
    def delete_lot_entirely(lot_id):
        lot = Lot(lot_id)

        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()

        lot.delete_entirely()

        return RestAPI.message(f'Lot {lot_id} is now deleted from archive.')

    @staticmethod
    @route('lots/personal/<int:lot_id>/request/guarantee', methods=['PUT'])
    @user.login_required
    @weighted(weight=1)
    def request_club_garantee(lot_id):
        lot = Lot(lot_id)

        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()

        try:
            value = RestAPI.request_data_to_json(request.data)['value']
        except APIExceptions.NoJsonError, KeyError:
            value = True
        
        if value:
            lot.request_for_guarantee()
            return RestAPI.message('A request for a club garantee is sent.'), 201
        else:
            lot.remove_request_for_guarantee()
            return RestAPI.message('A request for a club garantee is now removed.'), 201
        

    @staticmethod
    @route('lots/personal/<int:lot_id>/request/verify_security', methods=['PUT'])
    @user.login_required
    @weighted(weight=1)
    def request_security_verification(lot_id):
        lot = Lot(lot_id)

        if not lot.can_user_edit(user.email()):
            raise APIExceptions.NoPermissionError()

        try:
            value = RestAPI.request_data_to_json(request.data)['value']
        except APIExceptions.NoJsonError, KeyError:
            value = True
        
        if value:
            lot.request_for_security_verification()
            return RestAPI.message('A request for a security verification is sent.'), 201
        else:
            lot.remove_request_for_security_verification()
            return RestAPI.message('A request for a security verification is now removed.'), 201

    @staticmethod
    @route('lots/subscription/<int:lot_id>', methods=['PUT'])
    @user.login_required
    @weighted(weight=1)
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
    @weighted(weight=1)
    def unsubscribe_from_lot(lot_id):
        try:
            user.unsubscribe_from_lot(lot_id)
            return RestAPI.message(f'You are no longer subscribed to lot {lot_id}'), 201
        except:
            return RestAPI.message('You are not subscribed'), 200

    @staticmethod
    @route('lots/subscription', methods=['GET'])
    @user.login_required
    @weighted(weight=2)
    def get_subscribed_lots():
        return jsonify({'lots': user.get_subscriptions()}), 200

    # -------------------------------------------------------------------------
    # Moderator stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('lots/<int:lot_id>/approve', methods=['PUT'])
    @moderator.login_required
    @weighted(weight=1)
    def approve_lot(lot_id):
        Lot(lot_id).approve()
        return RestAPI.message('A lot is now approved'), 201

    @staticmethod
    @route('lots/<int:lot_id>/security', methods=['PUT', 'DELETE'])
    @moderator.login_required
    @weighted(weight=1)
    def set_security_checked(lot_id):
        lot = Lot(lot_id)
        if request.type == 'PUT':
            lot.set_security_checked(True)
            return RestAPI.message('Lot\'s security is now checked'), 201
        if request.type == 'DELETE':
            lot.set_security_checked(False)
            return RestAPI.message('Lot\'s security is no more checked'), 201

    @staticmethod
    @route('lots/<int:lot_id>/guarantee', methods=['PUT'])
    @moderator.login_required
    @weighted(weight=1)
    def set_guarantee(lot_id):
        if not request.json or not request.content_type.startswith('application/json'):
            raise APIExceptions.NoJsonError()

        RestAPI.check_required_fields(request.json, ['value'])

        value = request.json['value']
        lot = Lot(lot_id)
        lot.set_guarantee_value(value)
        lot.remove_request_for_guarantee()
        return RestAPI.message(f'Lot\'s guarantee is now {value}%'), 201

    @staticmethod
    @route('lots/<int:lot_id>/guarantee', methods=['DELETE'])
    @moderator.login_required
    @weighted(weight=1)
    def remove_guarantee(lot_id):
        lot = Lot(lot_id)
        lot.set_guarantee_value(0)
        return RestAPI.message('Lot\'s guarantee is now 0%'), 201

    @staticmethod
    @route('lots/requested/guarantee', methods=['GET', 'POST'])
    @moderator.login_required
    @weighted(weight=3)
    def get_guarantee_requested_lots():
        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(Lot.get_requested_for_guarantee(lot_filter)), 200

    @staticmethod
    @route('lots/requested/security_verification', methods=['GET', 'POST'])
    @moderator.login_required
    @weighted(weight=3)
    def get_security_requested_lots():
        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(Lot.get_requested_for_security_verification(lot_filter)), 200

    @staticmethod
    @route('lots/unapproved', methods=['GET', 'POST'])
    @moderator.login_required
    @weighted(weight=3)
    def get_unapproved_lots():
        try:
            request_json = RestAPI.request_data_to_json(request.data)
        except APIExceptions.NoJsonError:
            lot_filter = {}
        else:
            lot_filter = request_json['filter'] if 'filter' in request_json else {}

        return jsonify(Lot.get_all_unapproved_lots(lot_filter)), 200

    @staticmethod
    @route('lots/unapproved/<int:lot_id>', methods=['DELETE'])
    @moderator.login_required
    @weighted(weight=1)
    def remove_unapproved_lot(lot_id):
        required_fields = ['reason']

        RestAPI.check_required_fields(request.json, required_fields)

        reason = request.json['reason']
        lot = Lot(lot_id)
        lot.delete_lot_by_moderator(user.email(), reason)

        return RestAPI.message(f'Lot {lot_id} is now removed for a reason: {reason}')

    @staticmethod
    @route('lots/subscription/approved', methods=['GET'])
    @moderator.login_required
    @weighted(weight=1)
    def get_approved_subscriptions():
        return jsonify({'lots': Lot.get_approved_subscriptions()}), 200

    @staticmethod
    @route('lots/subscription/unapproved', methods=['GET'])
    @moderator.login_required
    @weighted(weight=1)
    def get_unapproved_subscriptions():
        return jsonify({'lots': Lot.get_unapproved_subscriptions()}), 200

    # -------------------------------------------------------------------------
    # Admin stuff
    # -------------------------------------------------------------------------

    @staticmethod
    @route('user/<string:email>/moderator', methods=['PUT', 'POST'])
    @administrator.login_required
    @weighted(weight=1)
    def give_moderator_rights(email):
        moderator.add(email)
        return RestAPI.message(f'{email} is now a moderator.')

    @staticmethod
    @route('user/<string:email>/moderator', methods=['DELETE'])
    @administrator.login_required
    @weighted(weight=1)
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