from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
import jwt

# initialize sql-alchemy
"""
position of this import really matters
"""
db = SQLAlchemy()

# local import
from config import app_config
from app.models import *

def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    """create user"""
    @app.route('/auth/register', methods=['POST'])
    def user_creation():
        email = str(request.data.get('email'))
        password = str(request.data.get('password'))
        user = User(email, password)
        user.save()
        response = jsonify({
        'id': user.id,
        'email': user.email
        })
        response.status_code = 201
        return response

    """login user"""
    @app.route('/auth/login', methods=['POST'])
    def user_login():
        # first check if user with email exists
        user = User.query.filter_by(email=request.data.get('email')).first()
        if user and user.password_is_valid(request.data.get('password')):
            # correct credentials
            # generate access token. this will be used as the authorization header
            access_token = user.generate_token(user.id)
            if access_token:
                response = {
                    'message': 'You logged in successfully',
                    'access_token': access_token.decode()
                }
                return response
        else:
            # user does not exists
            response = {
                'message': 'Verify credentials and try again'
            }
            return response

    """create, and retrieve bucketlists"""
    @app.route('/bucketlists/', methods=['POST', 'GET'])
    def bucketlists():
        if request.method == "POST":
            # create bucketlists
            name = str(request.data.get('name', ''))
            if name:
                bucketlist = Bucketlist(name=name)
                bucketlist.save()
                response = jsonify({
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                })
                response.status_code = 201
                return response
        else:
            # GET all bucketlists
            bucketlists = Bucketlist.get_all()
            results = []

            for bucketlist in bucketlists:
                obj = {
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    """edit, delete bucketlist"""
    @app.route('/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_manipulation(id, **kwargs):
     # retrieve a buckelist using it's ID
        bucketlist = Bucketlist.query.filter_by(id=id).first()
        if not bucketlist:
            return {
                "message": "no bucketlist with id: {}".format(id)
            }, 404

        if request.method == 'DELETE':
            # delete bucketlist
            bucketlist.delete()
            return {
                "message": "bucketlist {} deleted successfully".format(bucketlist.id)
             }, 200

        elif request.method == 'PUT':
            # edit bucketlist
            name = str(request.data.get('name', ''))
            bucketlist.name = name
            bucketlist.save()
            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified
            })
            response.status_code = 200
            return response
        else:
            # GET bucketlist by id
            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified
            })
            response.status_code = 200
            return response

    return app
