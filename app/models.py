# importing JSON Web Tokens
import jwt

from datetime import datetime, timedelta

from app import db
from flask import current_app
from flask_bcrypt import Bcrypt

class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    bucketlists = db.relationship(
        'Bucketlist', backref='users', lazy=True
    )

    def __init__(self, email, password):
        """Initialize the user with an email and a password."""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, id):
        """generates the access token"""

        try:
            # setup a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=5),
                'iat': datetime.utcnow(),
                'sub': id
            }
            # create the bytestring token using the payload and the secret key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from then authorization header"""
        try:
            # try to decode the token using our secret variables
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"

    def __repr__(self):
        return "<User: {}>".format(self.email)

class Bucketlist(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items = db.relationship(
        'Item', backref='bucketlists', lazy=True
    )

    def __init__(self, name, user_id):
        """initialize with name and owner."""
        self.name = name
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Bucketlist.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist: {}>".format(self.name)

class Item(db.Model):
    """This class represents the items table."""

    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlists.id'), nullable=False)

    def __init__(self, name, bucketlist_id):
        """initialize with name and bucketlist"""
        self.name = name
        self.bucketlist_id = bucketlist_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Item: {}>".format(self.name)
