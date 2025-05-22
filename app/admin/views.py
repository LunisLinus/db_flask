from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from . import admin
from .. import db
from ..models.user import User
from ..models.company import Company, InsuranceType
from ..models.location import Settlement, PickupPoint
from ..models.vehicle import Car, Driver
from ..models.order import Order, Cargo, PaymentMethod, Trip, CargoTrip
from sqlalchemy.sql import func


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin_user():
            flash('Эта страница доступна только администраторам.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


@admin.before_request
def check_admin():
    """Проверка прав администратора перед каждым запросом"""
    if not current_user.is_authenticated or not current_user.is_admin_user():
        flash('У вас нет прав для доступа к этой странице', 'danger')
        return redirect(url_for('main.index'))


@admin.route('/')
@login_required
@admin_required
def index():
    """Главная страница административной панели"""
    return render_template('admin/index.html')


# User management
@admin.route('/users')
@login_required
@admin_required
def users():
    query = User.query

    # Применяем фильтры из параметров запроса
    first_name = request.args.get('first_name')
    if first_name:
        query = query.filter(User.first_name.ilike(f'%{first_name}%'))

    last_name = request.args.get('last_name')
    if last_name:
        query = query.filter(User.last_name.ilike(f'%{last_name}%'))

    email = request.args.get('email')
    if email:
        query = query.filter(User.email.ilike(f'%{email}%'))

    phone = request.args.get('phone')
    if phone:
        query = query.filter(User.phone.ilike(f'%{phone}%'))

    # Получаем отфильтрованный список пользователей
    users = query.all()
    return render_template('admin/users.html', users=users)


@admin.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.is_role = request.form.get('is_role')
        db.session.commit()
        flash('Пользователь успешно обновлен.')
        return redirect(url_for('admin.users'))
    return render_template('admin/users/edit.html', user=user)


# Company management
@admin.route('/companies')
@login_required
@admin_required
def companies():
    """Список компаний с фильтрацией"""
    query = Company.query

    # Применяем фильтры из параметров запроса
    name = request.args.get('name')
    if name:
        query = query.filter(Company.name.ilike(f'%{name}%'))

    description = request.args.get('description')
    if description:
        query = query.filter(Company.description.ilike(f'%{description}%'))

    website = request.args.get('website')
    if website:
        query = query.filter(Company.website.ilike(f'%{website}%'))

    # Получаем отфильтрованный список компаний
    companies = query.all()
    return render_template('admin/companies/index.html', companies=companies)


@admin.route('/companies/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_company():
    """Создание новой компании"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        website = request.form.get('website')
        logo_url = request.form.get('logo_url')

        if not name:
            flash('Название компании обязательно', 'danger')
            return redirect(url_for('admin.new_company'))

        company = Company(
            name=name,
            description=description,
            website=website,
            logo_url=logo_url
        )

        db.session.add(company)
        db.session.commit()
        flash('Компания успешно создана', 'success')
        return redirect(url_for('admin.companies'))

    return render_template('admin/companies/new.html')


@admin.route('/companies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_company(id):
    """Редактирование компании"""
    company = Company.query.get_or_404(id)

    if request.method == 'POST':
        company.name = request.form.get('name')
        company.description = request.form.get('description')
        company.website = request.form.get('website')
        company.logo_url = request.form.get('logo_url')

        db.session.commit()
        flash('Компания успешно обновлена', 'success')
        return redirect(url_for('admin.companies'))

    return render_template('admin/companies/edit.html', company=company)


@admin.route('/companies/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_company(id):
    """Удаление компании"""
    company = Company.query.get_or_404(id)

    try:
        db.session.delete(company)
        db.session.commit()
        flash('Компания успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении компании: {str(e)}', 'danger')

    return redirect(url_for('admin.companies'))


# Car management
@admin.route('/cars')
@login_required
@admin_required
def cars():
    """Список автомобилей с фильтрацией"""
    query = Car.query

    # Применяем фильтры из параметров запроса
    brand = request.args.get('brand')
    if brand:
        query = query.filter(Car.brand.ilike(f'%{brand}%'))

    model = request.args.get('model')
    if model:
        query = query.filter(Car.model.ilike(f'%{model}%'))

    license_plate = request.args.get('license_plate')
    if license_plate:
        query = query.filter(Car.license_plate.ilike(f'%{license_plate}%'))

    status = request.args.get('status')
    if status:
        query = query.filter(Car.status == status)

    # Получаем отфильтрованный список автомобилей
    cars = query.all()
    return render_template('admin/cars/index.html', cars=cars)


@admin.route('/cars/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_car():
    """Создание нового автомобиля"""
    if request.method == 'POST':
        brand = request.form.get('brand')
        model = request.form.get('model')
        license_plate = request.form.get('license_plate')
        year = request.form.get('year')
        capacity = request.form.get('capacity')
        status = request.form.get('status')

        if not brand or not model or not license_plate or not year or not capacity:
            flash('Марка, модель, гос. номер, год выпуска и грузоподъемность обязательны', 'danger')
            return redirect(url_for('admin.new_car'))

        car = Car(
            brand=brand,
            model=model,
            license_plate=license_plate,
            year=year,
            capacity=capacity,
            status=status
        )

        db.session.add(car)
        db.session.commit()
        flash('Автомобиль успешно создан', 'success')
        return redirect(url_for('admin.cars'))

    return render_template('admin/cars/new.html')


@admin.route('/cars/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_car(id):
    car = Car.query.get_or_404(id)
    if request.method == 'POST':
        car.brand = request.form.get('brand')
        car.model = request.form.get('model')
        car.license_plate = request.form.get('license_plate')
        car.year = request.form.get('year')
        car.capacity = request.form.get('capacity')
        car.volume = request.form.get('volume')
        car.status = request.form.get('status')
        db.session.commit()
        flash('Автомобиль успешно обновлен.')
        return redirect(url_for('admin.cars'))
    return render_template('admin/cars/edit.html', car=car)


# Driver management
@admin.route('/drivers')
@login_required
@admin_required
def drivers():
    """Список водителей с фильтрацией"""
    query = Driver.query

    # Применяем фильтры из параметров запроса
    first_name = request.args.get('first_name')
    if first_name:
        query = query.filter(Driver.first_name.ilike(f'%{first_name}%'))

    last_name = request.args.get('last_name')
    if last_name:
        query = query.filter(Driver.last_name.ilike(f'%{last_name}%'))

    phone = request.args.get('phone')
    if phone:
        query = query.filter(Driver.phone.ilike(f'%{phone}%'))

    license_number = request.args.get('license_number')
    if license_number:
        query = query.filter(Driver.license_number.ilike(f'%{license_number}%'))

    status = request.args.get('status')
    if status:
        query = query.filter(Driver.status == status)

    # Получаем отфильтрованный список водителей
    drivers = query.all()
    return render_template('admin/drivers/index.html', drivers=drivers)


@admin.route('/drivers/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_driver():
    """Создание нового водителя"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        license_number = request.form.get('license_number')
        status = request.form.get('status')
        age = request.form.get('age')
        experience = request.form.get('experience')

        if not full_name or not phone_number or not license_number:
            flash('ФИО, телефон и номер водительского удостоверения обязательны', 'danger')
            return redirect(url_for('admin.new_driver'))

        # Разделяем полное имя на имя и фамилию
        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        driver = Driver(
            first_name=first_name,
            last_name=last_name,
            phone=phone_number,
            license_number=license_number,
            status=status
        )

        db.session.add(driver)
        db.session.commit()
        flash('Водитель успешно создан', 'success')
        return redirect(url_for('admin.drivers'))

    return render_template('admin/drivers/new.html')


@admin.route('/drivers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_driver(id):
    driver = Driver.query.get_or_404(id)
    if request.method == 'POST':
        driver.first_name = request.form.get('first_name')
        driver.last_name = request.form.get('last_name')
        driver.license_number = request.form.get('license_number')
        driver.phone = request.form.get('phone')
        driver.email = request.form.get('email')
        driver.status = request.form.get('status')
        driver.car_id = request.form.get('car_id')
        db.session.commit()
        flash('Водитель успешно обновлен.')
        return redirect(url_for('admin.drivers'))
    cars = Car.query.all()
    return render_template('admin/drivers/edit.html', driver=driver, cars=cars)


# Order management
@admin.route('/orders')
@login_required
@admin_required
def orders():
    """Список заказов с фильтрацией"""
    query = Order.query

    # Применяем фильтры из параметров запроса
    status = request.args.get('status')
    if status:
        query = query.filter(Order.status == status)

    min_price = request.args.get('min_price')
    if min_price:
        query = query.filter(Order.price >= float(min_price))

    max_price = request.args.get('max_price')
    if max_price:
        query = query.filter(Order.price <= float(max_price))

    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Order.created_at >= start_date)

    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Order.created_at <= end_date)

    client_id = request.args.get('client_id')
    if client_id:
        query = query.filter(Order.client_id == int(client_id))

    delivery_address = request.args.get('delivery_address')
    if delivery_address:
        query = query.filter(Order.delivery_address.ilike(f'%{delivery_address}%'))

    pickup_point_id = request.args.get('pickup_point_id')
    if pickup_point_id:
        query = query.filter(Order.pickup_point_id == int(pickup_point_id))

    # Получаем отфильтрованный список заказов
    orders = query.all()
    clients = User.query.all()
    pickup_points = PickupPoint.query.all()
    return render_template('admin/orders.html',
                           orders=orders,
                           clients=clients,
                           pickup_points=pickup_points)


@admin.route('/orders/<int:id>')
@login_required
@admin_required
def view_order(id):
    order = Order.query.get_or_404(id)
    return render_template('admin/orders/show.html', order=order)


# Reports
@admin.route('/reports/orders')
@login_required
@admin_required
def order_report():
    # Get date range from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Query orders within date range
    query = Order.query
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)

    orders = query.all()

    # Calculate statistics
    total_orders = len(orders)
    total_price = sum(order.price or 0 for order in orders)

    return render_template('admin/reports/orders.html',
                           orders=orders,
                           total_orders=total_orders,
                           total_price=total_price)


@admin.route('/reports/cars')
@login_required
@admin_required
def car_report():
    # Get all cars
    cars = Car.query.all()

    # Calculate statistics
    cars_by_status = db.session.query(
        Car.status,
        func.count(Car.id).label('count')
    ).group_by(Car.status).all()

    # Get cars with drivers
    cars_with_drivers = db.session.query(
        Car, Driver
    ).join(Driver, Car.id == Driver.car_id).all()

    return render_template('admin/reports/cars.html',
                           cars=cars,
                           cars_by_status=cars_by_status,
                           cars_with_drivers=cars_with_drivers)


@admin.route('/insurance-types')
@login_required
@admin_required
def insurance_types():
    """Список типов страховок с фильтрацией"""
    query = InsuranceType.query

    # Применяем фильтры из параметров запроса
    type_name = request.args.get('type')
    if type_name:
        query = query.filter(InsuranceType.type.ilike(f'%{type_name}%'))

    description = request.args.get('description')
    if description:
        query = query.filter(InsuranceType.description.ilike(f'%{description}%'))

    min_price = request.args.get('min_price')
    if min_price:
        query = query.filter(InsuranceType.price >= float(min_price))

    max_price = request.args.get('max_price')
    if max_price:
        query = query.filter(InsuranceType.price <= float(max_price))

    company_id = request.args.get('company_id')
    if company_id:
        query = query.filter(InsuranceType.company_id == int(company_id))

    # Получаем отфильтрованный список типов страховок
    insurance_types = query.all()
    companies = Company.query.all()
    return render_template('admin/insurance_types/index.html',
                           insurance_types=insurance_types,
                           companies=companies)


@admin.route('/insurance-types/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_insurance_type():
    """Создание нового типа страховки"""
    if request.method == 'POST':
        company_id = request.form.get('company_id')
        type_name = request.form.get('type')
        description = request.form.get('description')
        price = request.form.get('price')

        if not company_id or not type_name:
            flash('Выберите компанию и укажите тип страховки', 'danger')
            return redirect(url_for('admin.new_insurance_type'))

        insurance = InsuranceType(
            company_id=company_id,
            type=type_name,
            description=description,
            price=price
        )

        db.session.add(insurance)
        db.session.commit()
        flash('Тип страховки успешно создан', 'success')
        return redirect(url_for('admin.insurance_types'))

    companies = Company.query.all()
    return render_template('admin/insurance_types/new.html', companies=companies)


@admin.route('/trips')
@login_required
@admin_required
def trips():
    """Список рейсов"""
    all_trips = Trip.query.all()
    return render_template('admin/trips/index.html', trips=all_trips)


@admin.route('/trips/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_trip():
    """Создание нового рейса"""
    if request.method == 'POST':
        departure_settlement_id = request.form.get('departure_settlement_id')
        arrival_settlement_id = request.form.get('arrival_settlement_id')
        driver_id = request.form.get('driver_id')
        car_id = request.form.get('car_id')
        departure_time = request.form.get('departure_time')
        arrival_time = request.form.get('arrival_time')

        if not all([departure_settlement_id, arrival_settlement_id, driver_id, car_id, departure_time]):
            flash('Пункты отправления и назначения, водитель, автомобиль и время отправления обязательны', 'danger')
            return redirect(url_for('admin.new_trip'))

        trip = Trip(
            departure_settlement_id=departure_settlement_id,
            arrival_settlement_id=arrival_settlement_id,
            driver_id=driver_id,
            car_id=car_id,
            departure_time=departure_time,
            arrival_time=arrival_time
        )

        db.session.add(trip)
        db.session.commit()
        flash('Рейс успешно создан', 'success')
        return redirect(url_for('admin.trips'))

    settlements = Settlement.query.all()
    drivers = Driver.query.filter_by(status='active').all()
    cars = Car.query.filter_by(status='active').all()
    return render_template('admin/trips/new.html', drivers=drivers, cars=cars, settlements=settlements)


@admin.route('/settlements')
@login_required
@admin_required
def settlements():
    """Список населенных пунктов"""
    all_settlements = Settlement.query.all()
    return render_template('admin/settlements/index.html', settlements=all_settlements)


@admin.route('/settlements/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_settlement():
    """Создание нового населенного пункта"""
    if request.method == 'POST':
        name = request.form.get('name')
        region = request.form.get('region')
        country = request.form.get('country', 'Россия')
        postal_code = request.form.get('postal_code')

        if not name or not region:
            flash('Название и регион обязательны', 'danger')
            return redirect(url_for('admin.new_settlement'))

        settlement = Settlement(
            name=name,
            region=region,
            country=country,
            postal_code=postal_code
        )

        db.session.add(settlement)
        db.session.commit()
        flash('Населенный пункт успешно создан', 'success')
        return redirect(url_for('admin.settlements'))

    return render_template('admin/settlements/new.html')


@admin.route('/pickup-points')
@login_required
@admin_required
def pickup_points():
    """Список пунктов выдачи с фильтрацией"""
    query = PickupPoint.query

    # Применяем фильтры из параметров запроса
    name = request.args.get('name')
    if name:
        query = query.filter(PickupPoint.name.ilike(f'%{name}%'))

    address = request.args.get('address')
    if address:
        query = query.filter(PickupPoint.address.ilike(f'%{address}%'))

    phone = request.args.get('phone')
    if phone:
        query = query.filter(PickupPoint.phone.ilike(f'%{phone}%'))

    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter(PickupPoint.is_active == (is_active.lower() == 'true'))

    settlement_id = request.args.get('settlement_id')
    if settlement_id:
        query = query.filter(PickupPoint.settlement_id == int(settlement_id))

    # Получаем отфильтрованный список пунктов выдачи
    pickup_points = query.all()
    settlements = Settlement.query.all()
    return render_template('admin/pickup_points/index.html',
                           pickup_points=pickup_points,
                           settlements=settlements)


@admin.route('/pickup-points/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_pickup_point():
    """Создание нового пункта выдачи"""
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        settlement_id = request.form.get('settlement_id')
        phone = request.form.get('phone')
        working_hours = request.form.get('working_hours')
        is_active = 'is_active' in request.form

        if not name or not address or not settlement_id:
            flash('Название, адрес и населенный пункт обязательны', 'danger')
            return redirect(url_for('admin.new_pickup_point'))

        pickup_point = PickupPoint(
            name=name,
            address=address,
            settlement_id=settlement_id,
            phone=phone,
            working_hours=working_hours,
            is_active=is_active
        )

        db.session.add(pickup_point)
        db.session.commit()
        flash('Пункт выдачи успешно создан', 'success')
        return redirect(url_for('admin.pickup_points'))

    settlements = Settlement.query.all()
    return render_template('admin/pickup_points/new.html', settlements=settlements)
