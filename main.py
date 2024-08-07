'''Sets up the main flask application, database, and table objects'''
from flask import Flask, jsonify
from sqlalchemy import MetaData
# TODO import this so I have to write auth.endpoints.bp since I plan to name endpoints for everything
from auth.src import endpoints
from db import init_db_connector, init_tables


app: Flask = Flask(__name__)
# TODO figure out how to import db with local path
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////Users/emmanuelbastidas/Documents/Programming-Projects/smart-home-system/database.db"
db_connector = init_db_connector(app=app)
meta_data = MetaData()
tables = init_tables(app=app, meta_data=meta_data, db=db_connector)
users_table = tables[0]
sessions_table = tables[1]


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


if __name__ == '__main__':
    app.run(debug=True)
