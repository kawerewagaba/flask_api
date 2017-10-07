from app import db

class Item(db.Model):
    """
    This class defines the items table
    """

    __tablename__ = 'items'

    # Defining the fields
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False, unique=True)
    bucketlist = db.Column(db.Integer, db.ForeignKey('bucketlists.id'), nullable=False)

    
