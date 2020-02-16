#!flask/bin/python
from flask import Flask, abort, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth
from lib.database_handler import DatadaseHandler

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'code': -1000, 'msg': 'An unknown error occured while processing the request.'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'code': -1001, 'msg': 'The stuff you requested for is not found.'}), 404)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'code': -1002, 'msg': 'You are not authorized to execute this request.'}), 403)

@auth.verify_password
def verify_password(email, password):
    database = DatadaseHandler()
    return database.check_password(email, password)

@app.route('/api/v1/ping', methods=['GET'])
def ping():
    return jsonify({}), 200

@app.route('/api/v1/testUser', methods=['GET'])
@auth.login_required
def check_user():
    return jsonify({'msg': 'Successful'}), 200

@app.route('/api/v1/register', methods=['POST'])
def register():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)

    from lib.util.exceptions import RegistrationError
    email = request.json['email']
    password = request.json['password']

    database = DatadaseHandler()
    try:
        database.create_user(
            email,
            password
        )
    except RegistrationError as e:
        return jsonify({'code': e.error_id, 'msg': e.args[0]}), 409

    return jsonify({'msg': 'New user created'}), 201

if __name__ == '__main__':
    app.run(debug=True)