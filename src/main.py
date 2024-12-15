'''Sets up the main flask application, database, and table objects'''
import os
from flask import Flask, jsonify
from src.models import db_connector


def create_app(data_base_uri):
    '''Inititalize flask app this is useful for testing'''
    app: Flask = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = data_base_uri #f'sqlite:///{DB_PATH}'
    db_connector.init_app(app)

    # create database tables only creates db if tables don't exist
    with app.app_context():
        db_connector.create_all()

    from src.auth.src import endpoints
    app.register_blueprint(endpoints.bp)

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

    return app
# error handlers for global app
############################################################################################





if __name__ == '__main__':
    DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
    app = create_app( f'sqlite:///{DB_PATH}')
    app.run(debug=True)