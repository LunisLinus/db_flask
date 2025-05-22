from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from . import reports
from .. import db
from ..models.order import Order, Cargo
from ..models.vehicle import Car, Driver
from ..models.location import Settlement, PickupPoint
from sqlalchemy import func


@reports.route('/')
@login_required
def index():
    return render_template('reports/index.html')


@reports.route('/orders')
@login_required
def order_statistics():
    # Get date range from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = Order.query

    # Apply date filters
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)

    # Get orders
    orders = query.all()

    # Calculate statistics
    total_orders = len(orders)
    total_price = sum(order.price or 0 for order in orders)

    # Orders by date
    orders_by_date = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('count')
    ).group_by('date').all()

    # Orders by status
    orders_by_status = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()

    return render_template('reports/orders.html',
                           total_orders=total_orders,
                           total_price=total_price,
                           orders_by_date=orders_by_date,
                           orders_by_status=orders_by_status)


@reports.route('/cargo')
@login_required
def cargo_statistics():
    # Get date range from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Base query
    query = Cargo.query.join(Order)

    # Apply date filters
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)

    # Get cargo
    cargos = query.all()

    # Calculate statistics
    total_cargos = len(cargos)
    total_weight = sum(cargo.weight or 0 for cargo in cargos)
    total_volume = sum(cargo.volume or 0 for cargo in cargos)

    # Cargo by type
    cargo_by_type = db.session.query(
        Cargo.cargo_type,
        func.count(Cargo.id).label('count'),
        func.sum(Cargo.weight).label('total_weight')
    ).group_by(Cargo.cargo_type).all()

    # Package types distribution
    package_types = db.session.query(
        Cargo.package_type,
        func.count(Cargo.id).label('count')
    ).group_by(Cargo.package_type).all()

    return render_template('reports/cargo.html',
                           total_cargos=total_cargos,
                           total_weight=total_weight,
                           total_volume=total_volume,
                           cargo_by_type=cargo_by_type,
                           package_types=package_types)


@reports.route('/vehicles')
@login_required
def vehicle_statistics():
    # Get cars and drivers
    cars = Car.query.all()
    drivers = Driver.query.all()

    # Calculate statistics
    cars_by_status = db.session.query(
        Car.status,
        func.count(Car.id).label('count')
    ).group_by(Car.status).all()

    drivers_by_status = db.session.query(
        Driver.status,
        func.count(Driver.id).label('count')
    ).group_by(Driver.status).all()

    return render_template('reports/vehicles.html',
                           cars=cars,
                           drivers=drivers,
                           cars_by_status=cars_by_status,
                           drivers_by_status=drivers_by_status)


@reports.route('/pickup-points')
@login_required
def pickup_point_statistics():
    # Get pickup points
    pickup_points = PickupPoint.query.all()

    # Orders by settlement
    orders_by_settlement = db.session.query(
        Settlement.name,
        func.count(Order.id).label('count')
    ).join(PickupPoint, PickupPoint.settlement_id == Settlement.id) \
        .join(Order, Order.delivery_address.like(f'%{PickupPoint.address}%')) \
        .group_by(Settlement.name).all()

    return render_template('reports/pickup_points.html',
                           pickup_points=pickup_points,
                           orders_by_settlement=orders_by_settlement)
