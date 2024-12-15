'''Module to create sessions'''
import uuid
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import Insert, Delete, Select, delete, select, insert, exc, join, Join
from sqlalchemy import exc
from src.models import Session, User


class SessionManager():
    '''class for creating and deleting sessions from the sessions table'''

    def __init__(self, db_connector: SQLAlchemy) -> None:
        # self.app = current_app
        self.db_connector = db_connector

    def create_new_session(self, user: User) -> str | None:
        '''create new session in session table and returns session id'''
        existing_user_session: bool = self.session_exists(username=user.username)
        new_session_id: str = self._create_session_id()
        new_user_session = Session(session_id=new_session_id, user_id=user.user_id, user=user)
        if not existing_user_session:
            try:
                self.db_connector.session.add(new_user_session)
                user.session = new_user_session
                self.db_connector.session.commit()
                return new_session_id

            except exc.SQLAlchemyError as e:
                self.db_connector.session.rollback()
                raise e

        # session already exist for user so do not make a new one
        return None


    def get_user_session_id(self, user: User) -> str | None:
        '''Returns the session id associated with the given user
           If the user does not have a current session active None is returned
        '''
        if self.session_exists(username=user.username):
            statement = (
                self.db_connector.select(Session)
                .join(Session.user)
                .where(User.username == user.username)
            )
            result = self.db_connector.session.execute(statement).scalar()

            if result is not None:
                return result
            else:
                return None

        else:
            return None


    # todo maybe returning booleans isnthe the best option
    # but I do need to notify the user if it failed
    # should I notify them why it failed though?
    # If I do tell them why should I pass that information back
    # or throw an error here?
    def delete_session(self, session_id: str) -> bool:
        '''Delete current session in session table. If it does not exist return
           false'''
        try:
            statement = self.db_connector.select(Session).where(Session.session_id == session_id)
            result = self.db_connector.session.execute(statement).scalar()
            self.db_connector.session.delete(result)
            self.db_connector.session.commit()
            return True
        except exc.SQLAlchemyError:
            self.db_connector.session.rollback()

        return False


    def session_exists(self, session_id: str | None = None, username: str | None = None) -> bool:
        '''Checks to see if a session exists linked to a user'''
        if session_id is not None or username is not None:
                if session_id is not None:
                    query_command = (
                                                self.db_connector.select(Session)
                                                .where(Session.session_id == session_id)
                                             )

                else:
                    query_command = (
                                                self.db_connector.select(Session)
                                                .join(Session.user)
                                                .where(User.username == username)
                                            )
                    
                query_result = self.db_connector.session.execute(query_command).scalar()
                return query_result is not None

        return False

   
    def _create_session_id(self) -> str:
        '''Creates unique and returns string version of it'''
        return str(uuid.uuid4())
