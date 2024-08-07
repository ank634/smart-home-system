'''endpoints for authorization system'''
from flask import Blueprint, abort, make_response, request, jsonify
from auth.src.registration_manager import RegistrationManager
from auth.src.login_manager import LoginManager
from main import db_connector, users_table, sessions_table


bp = Blueprint('auth', __name__, url_prefix='/auth')
login_manager = LoginManager(db_connector, users_table, sessions_table)
registration_manager = RegistrationManager(db_connector, users_table)


@bp.route('/login', methods=['POST'])
def login():
    '''login'''
    data = request.get_json()
    username: str = data['username']
    password: str = data['password']

    session_token: str | None = login_manager.login(username, password)

    if session_token is not None:
        response = make_response(jsonify(message='logged in'))
        response.set_cookie('session-id', session_token)
        return response
    else:
        abort(401, description='Unauthorized Access')


@bp.route('/logout', methods=['DELETE'])
def logout():
    '''logout'''
    session_id: str | None = request.cookies.get('session-id')

    if session_id is None:
        abort(400, description='Bad Request, user must provide session-id')

    is_logged_out = login_manager.log_out(session_id)

    if is_logged_out:
        response = make_response(jsonify(message='logged out'))
        response.set_cookie('session-id', '')
        return response

    abort(404, description='Bad request, user must be logged in')


@bp.route('/register', methods=['POST'])
def register():
    '''Adds new entry to user table if there isn't an
       existing entry in table with that username
    '''
    data = request.get_json()
    username: str = data['username']
    password: str = data['password']

    user_succesfully_registered = registration_manager.register_user(
        username, password)

    if user_succesfully_registered:
        response = make_response(jsonify(message='user sucessfuly registered'))
        return response

    else:
        abort(404)
