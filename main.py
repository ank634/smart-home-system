'''Sets up the main flask application, database, and table objects'''
from flask import Flask, jsonify
from sqlalchemy import MetaData
from db import init_db_connector, init_tables
import os
# TODO import this so I have to write auth.endpoints.bp since I plan to name endpoints for everything


app: Flask = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
print(DB_PATH)
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_PATH}'
db_connector = init_db_connector(app=app)
meta_data = MetaData()
tables = init_tables(app=app, meta_data=meta_data, db=db_connector)
users_table = tables[0]
sessions_table = tables[1]

from auth.src import endpoints
app.register_blueprint(endpoints.bp)

# error handlers for global app
############################################################################################


@app.errorhandler(405)
def method_not_allowed(e):
    '''error handler to return 401 errors in json instead of html'''
    return jsonify(error=str(e)), 405


@app.errorhandler(404)
def resource_not_found(e):
    '''error handler to return 404 errors in json instead of html'''
    return jsonify(error=str(e)), 404


@app.errorhandler(401)
def unauthorized_access(e):
    '''error handler to return 401 errors in json instead of html'''
    return jsonify(error=str(e)), 401


@app.errorhandler(400)
def bad_user_request(e):
    '''error handler to return 400 errors in json instead of html'''
    return jsonify(error=str(e)), 400


@app.errorhandler(500)
def internal_server_error(e):
    '''error handler to return 500 errors in json instead of html'''
    return jsonify(error=str(e)), 500

@app.errorhandler(415)
def unsupported_media_type_error(e):
    '''error handler to return 415 errors in json instead of html'''
    return jsonify(error=str(e)), 415


if __name__ == '__main__':
    app.run(debug=True)
