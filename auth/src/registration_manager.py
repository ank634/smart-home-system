'''Modules that help a user register to the application'''
import hashlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Insert, insert, select, exc


class RegistrationManager:
    '''Class responsible for register new users to user table'''

    def __init__(self, db_connector: SQLAlchemy, users_table) -> None:
        self.db_connector = db_connector
        self.users_table = users_table

    def user_exist(self, username: str) -> bool:
        '''Desc: Checks to see if the user already exists in the database'''
        if self.db_connector is None or self.users_table is None:
            raise RuntimeError('LoginManager is not initialized correctly.')

        with self.db_connector.engine.connect() as connection:
            query = select(self.users_table).where(
                self.users_table.c.user_name == username)  # building the query
            # actually executing query just fetch one row
            result = connection.execute(query).fetchone()

            return result is not None

    def register_user(self, username: str, password: str) -> bool:
        '''add new entry to user table if it does not exist already'''
        # TODO consider making an exception so can differentiate from null checking, empty username and password and user exist
        if len(username) == 0 or len(password) == 0 or username is None or password is None:
            return False

        if self.user_exist(username):
            return False

        hashed_password: str = hashlib.sha256(str.encode(password)).hexdigest()

        # establish connection to database
        try:
            with self.db_connector.engine.connect() as connection:
                insertion_command: Insert = insert(self.users_table).values(
                    user_name=username, password=hashed_password)
                connection.execute(insertion_command)  # execute the command
                connection.commit()  # this must be added to every command that muatates data
                return True
        
        except exc.SQLAlchemyError as e:
            connection.rollback()
            raise e
        
        return False
            
            
