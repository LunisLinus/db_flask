from datetime import datetime
from .. import db


class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    year = db.Column(db.Integer)
    capacity = db.Column(db.Float)  # Грузоподъемность в тоннах
    volume = db.Column(db.Float)  # Объем кузова в м³
    status = db.Column(db.String(20), default='available')  # available, in_use, maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    trips = db.relationship('Trip', backref='car', lazy='dynamic')
    drivers = db.relationship('Driver', backref='car', lazy='dynamic')

    @property
    def status_color(self):
        status_colors = {
            'available': 'success',
            'in_use': 'warning',
            'maintenance': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Car {self.brand} {self.model} ({self.license_plate})>'


class Driver(db.Model):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    status = db.Column(db.String(20), default='available')  # available, busy, off
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    trips = db.relationship('Trip', backref='driver', lazy='dynamic')

    @property
    def status_color(self):
        status_colors = {
            'available': 'success',
            'busy': 'warning',
            'off': 'secondary'
        }
        return status_colors.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Driver {self.first_name} {self.last_name}>'
