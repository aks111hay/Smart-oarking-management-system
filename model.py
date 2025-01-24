from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'),autoincrement = True)  

    parking_lot = db.relationship('ParkingLot', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'<User {self.name}, {self.email}, ParkingLot {self.parking_lot.lot_name}>'


class ParkingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String(20), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  
    exit_time = db.Column(db.DateTime)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)  
    
    parking_lot = db.relationship('ParkingLot', lazy=True)

    def __repr__(self):
        return f'<ParkingData {self.number_plate}, {self.entry_time}, {self.exit_time}>'

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer, nullable=False, default=50)

    parking_data = db.relationship('ParkingData',lazy=True)

    def __repr__(self):
        return f'<ParkingLot {self.lot_name}, {self.location}, Capacity: {self.capacity}>'
