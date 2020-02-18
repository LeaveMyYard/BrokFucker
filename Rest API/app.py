from flask import Flask, abort, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatadaseHandler
from lib.user import User as user
from lib.moderator import Moderator as moderator
from lib.lot import Lot
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
    # as a normal function, creating all the error handlers
    for ex in exceptions_dict:
        app.errorhandler(ex)(
            exceptions_dict[ex]
        )

    @staticmethod
    @route('ping', methods=['GET'])
    def ping():
        return jsonify({}), 200

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

        user.create(
            request.json['email'],
            request.json['password']
        )

        return jsonify({'msg': 'New user created'}), 201

    @staticmethod
    @route('createLot', methods=['POST'])
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

        return jsonify({'msg': 'New lot created'}), 201

    @staticmethod
    @route('lot/<int:lot_id>/approve', methods=['PUT'])
    @moderator.login_required
    def approve_lot(lot_id):
        Lot.approve(lot_id)
        return jsonify({}), 201

    @staticmethod
    @route('lot/<int:lot_id>/setSecurityChecked', methods=['PUT'])
    @moderator.login_required
    def set_security_checked(lot_id):
        Lot.set_security_checked(lot_id, True)
        return jsonify({}), 201

    @staticmethod
    @route('lot/<int:lot_id>/setSecurityUnchecked', methods=['PUT'])
    @moderator.login_required
    def set_security_unchecked(lot_id):
        Lot.set_security_checked(lot_id, False)
        return jsonify({}), 201

    @staticmethod
    @route('getApprovedLots', methods=['GET'])
    @user.login_required
    def get_approved_lots():
        return jsonify(Lot.get_all_approved_lots()), 200

    @staticmethod
    @route('getUnapprovedLots', methods=['GET'])
    @moderator.login_required
    def get_unapproved_lots():
        return jsonify(Lot.get_all_unapproved_lots()), 200

    @staticmethod
    @route('favoriteLots/<int:lot_id>', methods=['POST', 'PUT', 'DELETE'])
    @user.login_required
    def updateFavoriteLots(lot_id):
        if request.method == 'POST' or request.method == 'POST':
            user.add_lot_to_favorites(lot_id)
        if request.method == 'DELETE':
            user.remove_lot_from_favorites(lot_id)
        return jsonify({}), 201

    @staticmethod
    @route('favoriteLots', methods=['GET'])
    @user.login_required
    def getFavoriteLots():
        return jsonify(user.get_favorites()), 200

if __name__ == '__main__':
    app.run(debug=True)