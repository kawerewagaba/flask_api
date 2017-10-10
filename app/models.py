from app import db
from flask_bcrypt import Bcrypt # password hashing algorithm

class Item(db.Model):
    """
    This class defines the items table
    """

    __tablename__ = 'items'

    # Defining the fields
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False, unique=True)
    bucketlist = db.Column(db.Integer, db.ForeignKey('bucketlists.id'), nullable=False)

    def __init__(self, description):
        self.description = description

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Item: {}>'.format(self.description)

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

class Bucketlist(db.Model):
    """
    This class defines the bucketlists table
    """

    __tablename__ = 'bucketlists'

    # Defining the fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items = db.relationship('Item', backref='items', lazy=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, name):
        """
        Initialize with name
        """
        self.name = name

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
        return '<Bucketlist: {}>'.format(self.name)
