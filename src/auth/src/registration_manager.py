'''Modules that help a user register to the application'''
import hashlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Insert, insert, select, exc
from src.models import User


class RegistrationManager:
    '''Class responsible for register new users to user table'''

    def __init__(self, db_connector: SQLAlchemy) -> None:
        self.db_connector = db_connector


    def register_user(self, username: str, password: str) -> bool:
        '''add new entry to user table if it does not exist already'''
        # TODO consider making an exception so can differentiate from null checking, empty username and password and user exist
        if len(username) == 0 or len(password) == 0 or username is None or password is None:
            return False

        if self._user_exist(username):
            return False

        hashed_password: str = hashlib.sha256(str.encode(password)).hexdigest()

        try: 
            user = User(username=username, password=hashed_password)
            self.db_connector.session.add(user)
            self.db_connector.session.commit()
            return True
        
        except exc.SQLAlchemyError as e:
            self.db_connector.session.rollback()
            raise e
        
        
    def _user_exist(self, username: str) -> bool:
        '''Desc: Checks to see if the user already exists in the database''' 
        query = self.db_connector.select(User).where(User.username == username)
        result = self.db_connector.session.execute(query).scalar()
        return result is not None         
            
