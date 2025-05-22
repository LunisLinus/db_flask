from datetime import datetime
from .. import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=True)
    insurance_type_id = db.Column(db.Integer, db.ForeignKey('insurance_types.id'), nullable=True)
    pickup_point_id = db.Column(db.Integer, db.ForeignKey('pickup_points.id'), nullable=True)
    status = db.Column(db.String(20), default='new')  # new, in_progress, completed, cancelled
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Дополнительные поля для заказа
    delivery_address = db.Column(db.String(255))
    delivery_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    # Relationships
    cargos = db.relationship('Cargo', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    pickup_point = db.relationship('PickupPoint', backref='orders', lazy='joined')

    @property
    def status_color(self):
        status_colors = {
            'new': 'primary',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Order {self.id}>'


class Cargo(db.Model):
    __tablename__ = 'cargos'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Numeric(10, 2))
    volume = db.Column(db.Numeric(10, 2))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    cargo_type = db.Column(db.String(100))
    package_type = db.Column(db.String(100))

    # Relationships
    trips = db.relationship('CargoTrip', backref='cargo', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cargo {self.name}>'


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='payment_method', lazy='dynamic')

    def __repr__(self):
        return f'<PaymentMethod {self.name}>'


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime)
    departure_settlement_id = db.Column(db.Integer, db.ForeignKey('settlements.id'), nullable=False)
    arrival_settlement_id = db.Column(db.Integer, db.ForeignKey('settlements.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled

    # Relationships
    cargo_trips = db.relationship('CargoTrip', backref='trip', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def status_color(self):
        status_colors = {
            'scheduled': 'primary',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Trip {self.id}>'


class CargoTrip(db.Model):
    __tablename__ = 'cargo_trips'

    id = db.Column(db.Integer, primary_key=True)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.id', ondelete='CASCADE'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<CargoTrip {self.cargo_id} - {self.trip_id}>'
