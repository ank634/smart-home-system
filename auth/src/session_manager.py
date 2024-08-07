'''Module to create sessions'''
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Insert, Delete, Select, delete, select, insert


class SessionManager():
    '''class for creating and deleting sessions from the sessions table'''

    def __init__(self, db_connector: SQLAlchemy, sessions_table) -> None:
        # self.app = current_app
        self.db_connector = db_connector
        self.sessions_table = sessions_table

    def create_new_session(self, username: str) -> str | None:
        '''create new session in session table and returns session id'''
        existing_user_session: bool = self.session_exists(username=username)

        if not existing_user_session:
            with self.db_connector.engine.connect() as connection:
                new_session_id: str = self.create_session_id()
                sql_command: Insert = insert(self.sessions_table).values(
                    session_id=new_session_id, user_name=username)
                connection.execute(sql_command)
                connection.commit()

                return new_session_id

        # session already exist for user so do not make a new one
        return None

    def delete_session(self, session_id: str) -> bool:
        '''Delete current session. If it does not exist return
           false'''
        if self.session_exists(session_id=session_id):
            with self.db_connector.engine.connect() as connection:
                delete_command: Delete = delete(self.sessions_table).where(
                    self.sessions_table.c.session_id == session_id)
                result = connection.execute(delete_command)
                connection.commit()
                return result.rowcount > 0

        return False

    def session_exists(self, session_id: str | None = None, username: str | None = None) -> bool:
        '''Checks to see if a session exists linked to a user'''
        if session_id is not None or username is not None:
            with self.db_connector.engine.connect() as connection:
                if session_id is not None:
                    query_command: Select = select(self.sessions_table).where(
                        self.sessions_table.c.session_id == session_id)

                elif username is not None:
                    query_command: Select = select(self.sessions_table).where(
                        self.sessions_table.c.user_name == username)

                query_result = connection.execute(query_command).fetchone()
                return query_result is not None

        return False

    # TODO add a more secure random generation of session id
    def create_session_id(self) -> str:
        '''Creates unique and returns string version of it'''
        return str(uuid.uuid4())
