'''Module providing some helper functions to set up
   database objects
'''
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table


def init_tables(app, meta_data, db):
    '''init existing users and sessions table in the selected database
       TODO break this into two functions....
    '''
    with app.app_context():
        users_table = Table('users', meta_data, autoload_with=db.engine)
        sessions_table = Table('sessions', meta_data, autoload_with=db.engine)
    return (users_table, sessions_table)


def init_db_connector(app):
    '''init sql alchemy object which gives app config data to the database
       connector
    '''
    return SQLAlchemy(app)
