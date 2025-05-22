from .. import db


class Settlement(db.Model):
    __tablename__ = 'settlements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Россия')
    postal_code = db.Column(db.String(20))

    # Relationships
    pickup_points = db.relationship('PickupPoint', backref='settlement', lazy='dynamic', cascade='all, delete-orphan')
    trips_from = db.relationship('Trip', foreign_keys='Trip.departure_settlement_id', backref='departure_settlement',
                                 lazy='dynamic')
    trips_to = db.relationship('Trip', foreign_keys='Trip.arrival_settlement_id', backref='arrival_settlement',
                               lazy='dynamic')

    def __repr__(self):
        return f'<Settlement {self.name}>'


class PickupPoint(db.Model):
    __tablename__ = 'pickup_points'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    settlement_id = db.Column(db.Integer, db.ForeignKey('settlements.id', ondelete='CASCADE'), nullable=False)
    phone = db.Column(db.String(20))
    working_hours = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

    def full_address(self):
        """Получить полный адрес пункта выдачи, включая населенный пункт"""
        return f"{self.settlement.name}, {self.address}"

    def __repr__(self):
        return f'<PickupPoint {self.name} ({self.settlement.name})>'
