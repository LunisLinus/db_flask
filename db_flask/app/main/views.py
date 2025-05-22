from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models.order import Order, Cargo
from ..models.vehicle import Car, Driver
from ..models.location import Settlement, PickupPoint
from ..models.company import InsuranceType
from sqlalchemy import or_, and_

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin_user():
        # Admin dashboard
        total_orders = Order.query.count()
        total_cars = Car.query.count()
        total_drivers = Driver.query.count()
        total_pickup_points = PickupPoint.query.count()
        
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        recent_cars = Car.query.order_by(Car.created_at.desc()).limit(5).all()
        
        return render_template('dashboard/admin.html',
                             total_orders=total_orders,
                             total_cars=total_cars,
                             total_drivers=total_drivers,
                             total_pickup_points=total_pickup_points,
                             recent_orders=recent_orders,
                             recent_cars=recent_cars)
    else:
        # User dashboard
        user_orders = Order.query.filter_by(client_id=current_user.id)\
            .order_by(Order.created_at.desc()).limit(5).all()
        
        return render_template('dashboard/user.html',
                             user_orders=user_orders)

@main.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Комплексная поисковая форма"""
    settlements = Settlement.query.all()
    pickup_points = PickupPoint.query.all()
    insurance_types = InsuranceType.query.all()
    
    if request.method == 'POST':
        # Получаем параметры поиска
        query = request.form.get('query', '')
        order_status = request.form.get('order_status', '')
        min_price = request.form.get('min_price', '')
        max_price = request.form.get('max_price', '')
        settlement_id = request.form.get('settlement_id', '')
        pickup_point_id = request.form.get('pickup_point_id', '')
        insurance_type_id = request.form.get('insurance_type_id', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        cargo_type = request.form.get('cargo_type', '')
        min_weight = request.form.get('min_weight', '')
        max_weight = request.form.get('max_weight', '')
        
        # Базовый запрос
        search_query = db.session.query(Order).join(Order.cargos, isouter=True)
        
        # Добавляем фильтры если они заданы
        filters = []
        
        # Поиск по общему запросу
        if query:
            filters.append(or_(
                Order.delivery_address.ilike(f'%{query}%'),
                Order.notes.ilike(f'%{query}%'),
                Cargo.name.ilike(f'%{query}%')
            ))
        
        # Фильтры по заказу
        if order_status:
            filters.append(Order.status == order_status)
        
        if min_price:
            filters.append(Order.price >= float(min_price))
        
        if max_price:
            filters.append(Order.price <= float(max_price))
        
        if settlement_id:
            # Поиск по населенному пункту через связанные пункты выдачи
            pickup_points_in_settlement = PickupPoint.query.filter_by(settlement_id=settlement_id).all()
            pickup_point_ids = [pp.id for pp in pickup_points_in_settlement]
            if pickup_point_ids:
                filters.append(Order.pickup_point_id.in_(pickup_point_ids))
        
        if pickup_point_id:
            filters.append(Order.pickup_point_id == pickup_point_id)
        
        if insurance_type_id:
            filters.append(Order.insurance_type_id == insurance_type_id)
        
        if start_date:
            filters.append(Order.created_at >= start_date)
        
        if end_date:
            filters.append(Order.created_at <= end_date)
        
        # Фильтры по грузам
        if cargo_type:
            filters.append(Cargo.cargo_type == cargo_type)
        
        if min_weight:
            filters.append(Cargo.weight >= float(min_weight))
        
        if max_weight:
            filters.append(Cargo.weight <= float(max_weight))
        
        # Применяем все фильтры
        if filters:
            search_query = search_query.filter(and_(*filters))
        
        # Для обычных пользователей показываем только их заказы
        if not current_user.is_admin_user():
            search_query = search_query.filter(Order.client_id == current_user.id)
        
        # Получаем результаты
        search_results = search_query.distinct().all()
        
        return render_template('main/search_results.html', 
                               orders=search_results,
                               query=query,
                               settlements=settlements,
                               pickup_points=pickup_points,
                               insurance_types=insurance_types)
    
    return render_template('main/search.html', 
                          settlements=settlements,
                          pickup_points=pickup_points,
                          insurance_types=insurance_types)

@main.route('/api/pickup-points-by-settlement/<int:settlement_id>')
@login_required
def pickup_points_by_settlement(settlement_id):
    """API для получения пунктов выдачи по населенному пункту"""
    pickup_points = PickupPoint.query.filter_by(settlement_id=settlement_id, is_active=True).all()
    return jsonify([{
        'id': pp.id,
        'name': pp.name,
        'address': pp.address,
        'phone': pp.phone,
        'working_hours': pp.working_hours
    } for pp in pickup_points]) 