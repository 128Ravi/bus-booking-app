from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    from_city = db.Column(db.String(80))
    to_city = db.Column(db.String(80))
    total_seats = db.Column(db.Integer)
    available_seats = db.Column(db.Integer)
    price = db.Column(db.Integer)  # price per seat

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer)
    passenger_name = db.Column(db.String(80))
    travel_date = db.Column(db.String(20))
    seats = db.Column(db.String(200))
    amount_paid = db.Column(db.Integer)