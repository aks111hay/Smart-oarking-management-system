from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'))  # Removed autoincrement

    parking_lot = db.relationship('ParkingLot', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'<User {self.name}, {self.email}, ParkingLot ID {self.parking_lot_id}>'


class ParkingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String(20), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)

    parking_lot = db.relationship('ParkingLot', backref=db.backref('parking_data', lazy='dynamic'))  # Adjusted lazy loading

    def __repr__(self):
        return f'<ParkingData {self.number_plate}, Entry: {self.entry_time}, Exit: {self.exit_time}>'


class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_name = db.Column(db.String(100), nullable=False)  # Added field for lot name
    location = db.Column(db.String(255), nullable=False)  # Added field for location
    capacity = db.Column(db.Integer, nullable=False, default=50)

    def __repr__(self):
        return f'<ParkingLot {self.lot_name}, Location: {self.location}, Capacity: {self.capacity}>'
