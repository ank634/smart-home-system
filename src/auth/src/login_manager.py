'''Module thats meant to encapsulate login and logout functionalities'''
import hashlib
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from src.auth.src.session_manager import SessionManager
from src.models import User


class LoginManager:
    '''class to encapsulate login and logout functionality'''

    def __init__(self, db_connector: SQLAlchemy) -> None:
        self.db_connector = db_connector
        self.session_manager = SessionManager(self.db_connector)
        self.app = current_app


    def login(self, username: str, password: str) -> str | None:
        '''Creates a new session token for user in session table if credentials are valid
           if session token already exist user is given the current session token
        '''
        hashed_password = hashlib.sha256(str.encode(password)).hexdigest()

        if self._user_exist(username=username):
            query = self.db_connector.select(User).where(
                User.username == username).where(
                User.password == hashed_password)  # building the query

            result: User = self.db_connector.session.execute(query).scalar()
            if result is not None and not self._is_logged_in_username(username=username):
                session_created = self.session_manager.create_new_session(result)
                return session_created
            elif result is not None and self._is_logged_in_username(username=username):
                return self.session_manager.get_user_session_id(result).session_id

        else:
            return None


    # Same issue should I tell them why they couldn't log out?
    def log_out(self, session_token: str) -> bool:
        '''Log user out by deleting their session token from the session table'''
        return self.session_manager.delete_session(session_token)


    def _is_logged_in_username(self, username: str) -> bool:
        '''Desc: Checks to see if there is a current session ID for given user
           Param: username the username you want to check if they have a current session ID
           Return: boolean if true or false if there exist a valid session ID 
        '''
        if username is None:
            raise TypeError('username must not be None')

        return self.session_manager.session_exists(username=username)


    def _is_logged_in_session_id(self, session_id: str) -> bool:
        '''Desc: Checks to see if the passed in session-id is still current
           Param: session-id you want to check
           Return: boolean check to see whever session-id is valid or not
        '''
        if session_id is None:
            raise TypeError('session-id must not be None')

        return self.session_manager.session_exists(session_id=session_id)


    def _user_exist(self, username: str) -> bool:
        '''Desc: Checks to see if the user already exists in the database'''
        if self.db_connector is None:
            raise RuntimeError('LoginManager is not initialized correctly.')
 
        query = self.db_connector.select(User).where(User.username == username)
        result = self.db_connector.session.execute(query).scalar()
        return result is not None