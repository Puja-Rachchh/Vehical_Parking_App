
from config import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



class User( UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(32), unique=True, nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(6))
    is_admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128), nullable=False)
    reservations = db.relationship('ReserveParking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, 
                                  cascade='all, delete-orphan')


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # 'O' for Occupied, 'A' for Available
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('ReserveParking', backref='parking_spot', lazy=True)

    def __init__(self, lot_id, spot_number):
        self.lot_id = lot_id
        self.spot_number = spot_number
        self.status = 'A'


class ReserveParking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)  # Will be calculated when parking is completed
    vehicle_number = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # To track current vs historical reservations


class ParkingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Store lot information at the time of reservation
    lot_name = db.Column(db.String(100), nullable=False)
    lot_address = db.Column(db.String(200), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    
    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    
    # Timing and cost information
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=False)
    parking_cost = db.Column(db.Float, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='parking_history', lazy=True)



