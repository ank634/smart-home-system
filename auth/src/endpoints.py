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

    # check if payload has right values
    if 'username' not in data or 'password' not in data:
        abort(400, description='must include username and password in json body')

    username: str = data['username']
    password: str = data['password']

    session_token: str | None
    try:
        session_token = login_manager.login(username, password)

    except Exception:
        abort(500, description='Login failed due to an error on our end')

    if session_token is not None:
        response = make_response(jsonify(message='logged in'))
        response.set_cookie('session-id', session_token)
        return response

    abort(401, description='Unauthorized Access, invalid credentials')


@bp.route('/logout', methods=['DELETE'])
def logout():
    '''logout'''
    session_id: str | None = request.cookies.get('session-id')

    # TODO check if this is an empty string or actually None
    if session_id is None:
        abort(400, description='Bad Request, user must provide session-id')

    try:
        is_logged_out = login_manager.log_out(session_id)

        if is_logged_out:
            response = make_response(jsonify(message='logged out'))
            response.set_cookie('session-id', '')
            return response

    except Exception:
        abort(500, description='Logout failed due to an error on our end')

    abort(404, description='Bad request, user must be logged in')


@bp.route('/register', methods=['POST'])
def register():
    '''Adds new entry to user table if there isn't an
       existing entry in table with that username
    '''
    data = request.get_json()

    # check if payload has right values
    if 'username' not in data or 'password' not in data:
        abort(400, description='must include username and password in json body')

    username: str = data['username']
    password: str = data['password']

    try:
        user_succesfully_registered = registration_manager.register_user(
            username, password)

        if user_succesfully_registered:
            response = make_response(
                jsonify(message='user sucessfuly registered'))
            return response

    except Exception:
        abort(500, description='Registration failed due to an error on our end')

    abort(404)
