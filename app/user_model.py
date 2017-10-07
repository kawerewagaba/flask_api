from app import db, Bucketlist
from flask_bcrypt import Bcrypt # password hashing algorithm

class User(db.Model):
    """
    This class defines the users table
    """

    __tablename__ = 'users'

    # Define the fields of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    bucketlists = db.relationship('Bucketlist', backref='bucketlists', lazy=True)

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

    def __repr__(self):
        return '<User: {}>'.format(self.email)
