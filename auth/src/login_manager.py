'''Module thats meant to encapsulate login and logout functionalities'''
import hashlib
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from auth.src.session_manager import SessionManager


class LoginManager:
    '''class to encapsulate login and logout functionality'''

    def __init__(self, db_connector: SQLAlchemy, users_table, sessions_table) -> None:
        self.db_connector = db_connector
        self.users_table = users_table
        self.sessions_table = sessions_table
        self.session_manager = SessionManager(
            self.db_connector, self.sessions_table)
        self.app = current_app

    def user_exist(self, username: str) -> bool:
        '''Checks to see if the user exist in the Users table'''
        if self.db_connector is None or self.users_table is None:
            raise RuntimeError('LoginManager is not initialized correctly.')

        # query and return if there were any results
        with self.db_connector.engine.connect() as connection:
            query = select(self.users_table).where(
                self.users_table.columns.user_name == username)
            result = connection.execute(query).fetchone()

            return result is not None

    def login(self, username: str, password: str) -> str | None:
        '''Creates a new session token for user in session table if credentials are valid
           if session token already exist user is not logged in
        '''
        hashed_password = hashlib.sha256(str.encode(password)).hexdigest()
        # if the user name is valid and they are currently logged in
        if not self.is_logged_in_username(username):
            with self.db_connector.engine.connect() as connection:
                query = select(self.users_table).where(
                    self.users_table.c.user_name == username).where(
                    self.users_table.c.password == hashed_password)  # building the query

                result = connection.execute(query).fetchone()
                if result is not None:
                    session_created = self.session_manager.create_new_session(
                        username)
                    return session_created
                else:
                    return None
        # could not log user in. Either they are already logged in or user does not exist
        # maybe let the user log in anyway but log them out of exisiting sessions
        else:
            return None

    def log_out(self, session_token: str) -> bool:
        '''Log user out by deleting their session token from the session table'''
        return self.session_manager.delete_session(session_id=session_token)

    def is_logged_in_username(self, username: str) -> bool:
        '''Desc: Checks to see if there is a current session ID for given user
           Param: username the username you want to check if they have a current session ID
           Return: boolean if true or false if there exist a valid session ID 
        '''
        if username is None:
            raise TypeError('username must not be None')

        return self.session_manager.session_exists(username=username)

    def is_logged_in_session_id(self, session_id: str) -> bool:
        '''Desc: Checks to see if the passed in session-id is still current
           Param: session-id you want to check
           Return: boolean check to see whever session-id is valid or not
        '''
        if session_id is None:
            raise TypeError('session-id must not be None')

        return self.session_manager.session_exists(session_id=session_id)
