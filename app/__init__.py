from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
import jwt
from flask_bcrypt import Bcrypt

# in memory store for revoked tokens
revoked_tokens = []

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
                }, 200
                return response
        else:
            # user does not exists
            response = {
                'message': 'Verify credentials and try again'
            }, 401
            return response

    """ logout user """
    @app.route('/auth/logout', methods=['POST'])
    def user_logout():
        try:
            #get the access token from the request
            access_token = request.data.get('access_token')
            if access_token:
                revoked_tokens.append(access_token)
                return {'message': 'You logged out successfully'}
        except Exception as e:
            # something went wrong on the server side
            return {'Error': e}

    """ reset password """
    @app.route('/auth/reset-password', methods=['POST'])
    def reset_password():
        try:
            access_token = request.data.get('access_token')
            if access_token:
                user_id = User.decode_token(access_token)
                if not isinstance(user_id, str):
                    new_pass = request.data.get('password')
                    if new_pass:
                        user = User.query.filter_by(id=user_id).first()
                        if user:
                            # hash new password
                            user.password = Bcrypt().generate_password_hash(password=new_pass).decode()
                            user.save()
                            return {'message': 'Password reset successfully'}, 200
            else:
                #user not legit
                return {'Authentication': 'You are not authorized to access this page'}, 401

        except Exception as e:
            # something went wrong on the server side
            return {'Error': e}

    """create, and retrieve bucketlists"""
    @app.route('/bucketlists/', methods=['POST', 'GET'])
    def bucketlists():
        try:
            # get the access token from the header
            access_token = request.headers.get('Authorization')
            if access_token and access_token not in revoked_tokens:
                # attempt to decode the token and get the user id
                user_id = User.decode_token(access_token)
                if not isinstance(user_id, str):
                    # returned ID is an int
                    # go ahead and handle the request, user is authenticated
                    if request.method == "POST":
                        # create bucketlists
                        name = str(request.data.get('name', ''))
                        if name:
                            bucketlist = Bucketlist(name=name, user_id=user_id)
                            bucketlist.save()
                            response = jsonify({
                                'id': bucketlist.id,
                                'name': bucketlist.name,
                                'date_created': bucketlist.date_created,
                                'date_modified': bucketlist.date_modified,
                                'created_by': user_id
                            })
                            response.status_code = 201
                            return response
                    else:
                        # GET all bucketlists
                        bucketlists = Bucketlist.query.filter_by(user_id=user_id)
                        results = []

                        for bucketlist in bucketlists:
                            obj = {
                                'id': bucketlist.id,
                                'name': bucketlist.name,
                                'date_created': bucketlist.date_created,
                                'date_modified': bucketlist.date_modified,
                                'created_by': user_id
                            }
                            results.append(obj)
                        response = jsonify(results)
                        response.status_code = 200
                        return response
                else:
                    # authentication failure
                    # user_id returns the output from the decode function
                    return {'Error': user_id}
            else:
                #user not legit
                return {'Authentication': 'You are not authorized to access this page'}, 401

        except Exception as e:
            # something went wrong on the server side
            return {'Error': e}

    """edit, delete bucketlist"""
    @app.route('/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_manipulation(id, **kwargs):
        try:
            # get the access token from the header
            access_token = request.headers.get('Authorization')
            if access_token and access_token not in revoked_tokens:
                # attempt to decode the token and get the user id
                user_id = User.decode_token(access_token)
                if not isinstance(user_id, str):
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
                            'date_modified': bucketlist.date_modified,
                            'created_by': user_id
                        })
                        response.status_code = 200
                        return response
                    else:
                        # GET bucketlist by id
                        response = jsonify({
                            'id': bucketlist.id,
                            'name': bucketlist.name,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified,
                            'created_by': user_id
                        })
                        response.status_code = 200
                        return response
                else:
                    # authentication failure
                    return {'Error': user_id}
            else:
                return {'Authentication': 'You are not authorized to access this page'}, 401
        except:
            # user is not legit
            return {'Authentication': 'You are not authorized to access this page'}

    """ add and view items """
    @app.route('/bucketlists/<int:id>/items/', methods=['POST', 'GET'])
    def add_item(id):
        try:
            # get the access token from the header
            access_token = request.headers.get('Authorization')
            if access_token and access_token not in revoked_tokens:
                # attempt to decode the token and get the user id
                user_id = User.decode_token(access_token)
                if not isinstance(user_id, str):
                    # returned ID is an int
                    # go ahead and handle the request, user is authenticated
                    if request.method == 'POST':
                        name = str(request.data.get('name'))
                        if name:
                            item = Item(name=name, bucketlist_id=id)
                            item.save()
                            response = jsonify({
                                'id': item.id,
                                'name': item.name,
                                'date_created': item.date_created,
                                'bucketlist_id': id
                            })
                            response.status_code = 201
                            return response
                    elif request.method == 'GET':
                        items = Item.query.filter_by(bucketlist_id=id)
                        results = []
                        for item in items:
                            obj = {
                                'id': item.id,
                                'name': item.name,
                                'date_created': item.date_created,
                                'bucketlist_id': id
                            }
                            results.append(obj)
                        response = jsonify(results)
                        response.status_code = 200
                        return response
                else:
                    # authentication failure
                    # user_id returns the output from the decode function
                    return {'Error': user_id}
            else:
                return {'Authentication': 'You are not authorized to access this page'}, 401
        except Exception as e:
            return {'Error': e}

    """ edit and delete item """
    @app.route('/bucketlists/<int:bucketlist_id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def item_edit_or_delete(bucketlist_id, item_id):
        try:
            # get the access token from the header
            access_token = request.headers.get('Authorization')
            if access_token and access_token not in revoked_tokens:
                # attempt to decode the token and get the user id
                user_id = User.decode_token(access_token)
                if not isinstance(user_id, str):
                    # returned ID is an int
                    # go ahead and handle the request, user is authenticated
                    item = Item.query.filter_by(id=item_id).first()
                    if not item:
                        return {'message': 'No item with id {}'.format(item_id)}, 404
                    else:
                        if request.method == 'PUT':
                            # edit item
                            name = str(request.data.get('name'))
                            if name:
                                item.name = name
                                item.save()
                                response = jsonify({
                                    'id': item.id,
                                    'name': item.name,
                                    'date_created': item.date_created,
                                    'bucketlist_id': bucketlist_id
                                })
                                response.status_code = 201
                                return response
                        elif request.method == 'DELETE':
                            # delete item
                            item.delete()
                            return {'message': 'Item with id {} has been deleted.'.format(item_id)}, 200
                        else:
                            # get item by ID
                            response = jsonify({
                                'id': item.id,
                                'name': item.name,
                                'date_created': item.date_created,
                                'bucketlist_id': bucketlist_id
                            })
                            response.status_code = 200
                            return response
                else:
                    # authentication failure
                    # user_id returns the output from the decode function
                    return {'Error': user_id}
            else:
                return {'Authentication': 'You are not authorized to access this page'}, 401
        except Exception as e:
            return {'Error': e}

    return app
