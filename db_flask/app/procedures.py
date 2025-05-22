"""
Модуль с процедурами для логистической системы
Содержит Python-эквиваленты хранимых процедур SQL
"""

from sqlalchemy import text
from flask import current_app
from datetime import datetime, timedelta
from . import db
from .models.order import Order, Trip, Cargo, CargoTrip
from .models.vehicle import Car, Driver
from .models.location import Settlement, PickupPoint

def register_sql_functions(app):
    """Регистрация хранимых функций SQL в базе данных"""
    with app.app_context():
        # Функция расчета стоимости доставки груза
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION calculate_delivery_cost(
            cargo_weight NUMERIC,
            cargo_volume NUMERIC,
            distance NUMERIC,
            cargo_type VARCHAR
        ) RETURNS NUMERIC AS $$
        DECLARE
            base_cost NUMERIC := 500.0;  -- Базовая стоимость
            weight_cost NUMERIC := 100.0;  -- Стоимость за кг
            volume_cost NUMERIC := 500.0;  -- Стоимость за м³
            distance_cost NUMERIC := 15.0;  -- Стоимость за км
            type_multiplier NUMERIC := 1.0;  -- Множитель типа груза
            final_cost NUMERIC;
        BEGIN
            -- Множитель в зависимости от типа груза
            IF cargo_type = 'Хрупкий' THEN
                type_multiplier := 1.5;
            ELSIF cargo_type = 'Тяжелый' THEN
                type_multiplier := 1.3;
            ELSIF cargo_type = 'Опасный' THEN
                type_multiplier := 2.0;
            END IF;
            
            -- Расчет итоговой стоимости
            final_cost := base_cost + 
                        (cargo_weight * weight_cost) + 
                        (cargo_volume * volume_cost) + 
                        (distance * distance_cost);
            
            -- Применение множителя типа груза
            final_cost := final_cost * type_multiplier;
            
            RETURN final_cost;
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        # Функция для получения активных пунктов выдачи в населенном пункте
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION get_active_pickup_points(
            settlement_id INTEGER
        ) RETURNS TABLE (
            id INTEGER,
            name VARCHAR,
            address VARCHAR,
            phone VARCHAR,
            working_hours VARCHAR
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                pp.id,
                pp.name,
                pp.address,
                pp.phone,
                pp.working_hours
            FROM pickup_points pp
            WHERE pp.settlement_id = settlement_id AND pp.is_active = TRUE;
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        # Функция для подбора оптимального автомобиля для груза
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION find_optimal_car(
            cargo_weight NUMERIC,
            cargo_volume NUMERIC
        ) RETURNS INTEGER AS $$
        DECLARE
            car_id INTEGER;
        BEGIN
            -- Найти автомобиль с минимальной достаточной грузоподъемностью
            SELECT c.id INTO car_id
            FROM cars c
            WHERE c.status = 'active'
            AND c.capacity >= cargo_weight
            ORDER BY c.capacity ASC
            LIMIT 1;
            
            -- Если не найден подходящий автомобиль, вернуть NULL
            RETURN car_id;
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        # Функция для генерации отчета по заказам
        db.session.execute(text("""
        CREATE OR REPLACE FUNCTION generate_orders_report(
            start_date DATE,
            end_date DATE
        ) RETURNS TABLE (
            order_date DATE,
            order_count INTEGER,
            total_price NUMERIC,
            avg_price NUMERIC
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                DATE(o.created_at) as order_date,
                COUNT(o.id) as order_count,
                SUM(o.price) as total_price,
                AVG(o.price) as avg_price
            FROM orders o
            WHERE o.created_at BETWEEN start_date AND end_date
            GROUP BY DATE(o.created_at)
            ORDER BY order_date;
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        db.session.commit()


def calculate_delivery_cost(cargo_weight, cargo_volume, distance, cargo_type):
    """
    Расчет стоимости доставки груза (Python-вариант)
    
    Args:
        cargo_weight (float): Вес груза в кг
        cargo_volume (float): Объем груза в м³
        distance (float): Расстояние доставки в км
        cargo_type (str): Тип груза
        
    Returns:
        float: Стоимость доставки
    """
    base_cost = 500.0  # Базовая стоимость
    weight_cost = 100.0  # Стоимость за кг
    volume_cost = 500.0  # Стоимость за м³
    distance_cost = 15.0  # Стоимость за км
    type_multiplier = 1.0  # Множитель типа груза
    
    # Множитель в зависимости от типа груза
    if cargo_type == 'Хрупкий':
        type_multiplier = 1.5
    elif cargo_type == 'Тяжелый':
        type_multiplier = 1.3
    elif cargo_type == 'Опасный':
        type_multiplier = 2.0
    
    # Расчет итоговой стоимости
    final_cost = base_cost + \
                (cargo_weight * weight_cost) + \
                (cargo_volume * volume_cost) + \
                (distance * distance_cost)
    
    # Применение множителя типа груза
    final_cost = final_cost * type_multiplier
    
    return final_cost


def get_active_pickup_points(settlement_id):
    """
    Получение активных пунктов выдачи в населенном пункте (Python-вариант)
    
    Args:
        settlement_id (int): ID населенного пункта
        
    Returns:
        list: Список активных пунктов выдачи
    """
    return PickupPoint.query.filter_by(
        settlement_id=settlement_id,
        is_active=True
    ).all()


def find_optimal_car(cargo_weight, cargo_volume):
    """
    Подбор оптимального автомобиля для груза (Python-вариант)
    
    Args:
        cargo_weight (float): Вес груза в кг
        cargo_volume (float): Объем груза в м³
        
    Returns:
        Car: Оптимальный автомобиль или None
    """
    return Car.query.filter_by(status='active')\
        .filter(Car.capacity >= cargo_weight)\
        .order_by(Car.capacity.asc())\
        .first()


def find_available_driver():
    """
    Поиск доступного водителя для рейса
    
    Returns:
        Driver: Доступный водитель или None
    """
    return Driver.query.filter_by(status='active').first()


def generate_orders_report(start_date, end_date):
    """
    Генерация отчета по заказам за период (Python-вариант)
    
    Args:
        start_date (datetime): Начальная дата
        end_date (datetime): Конечная дата
        
    Returns:
        dict: Отчет по заказам
    """
    from sqlalchemy import func
    
    # Запрос статистики по датам
    daily_stats = db.session.query(
        func.date(Order.created_at).label('order_date'),
        func.count(Order.id).label('order_count'),
        func.sum(Order.price).label('total_price'),
        func.avg(Order.price).label('avg_price')
    ).filter(
        Order.created_at.between(start_date, end_date)
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()
    
    # Агрегированная статистика
    total_orders = sum(day.order_count for day in daily_stats)
    total_revenue = sum(day.total_price for day in daily_stats)
    avg_order_price = total_revenue / total_orders if total_orders else 0
    
    return {
        'daily_stats': daily_stats,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_price': avg_order_price
    }


def calculate_optimal_route(pickup_point_id, delivery_address):
    """
    Расчет оптимального маршрута доставки (эмуляция)
    
    Args:
        pickup_point_id (int): ID пункта выдачи
        delivery_address (str): Адрес доставки
        
    Returns:
        dict: Оптимальный маршрут
    """
    # В реальной системе здесь был бы вызов API картографического сервиса
    # Эмулируем расчет маршрута для демонстрации
    pickup_point = PickupPoint.query.get(pickup_point_id)
    
    if not pickup_point:
        return {
            'success': False,
            'error': 'Пункт выдачи не найден'
        }
    
    # Эмуляция расчета расстояния
    import random
    distance = random.uniform(5.0, 50.0)
    duration = distance * 2  # Примерно 30 км/ч
    
    return {
        'success': True,
        'distance': round(distance, 2),  # км
        'duration': round(duration, 2),  # мин
        'pickup_point': {
            'name': pickup_point.name,
            'address': pickup_point.address,
            'settlement': pickup_point.settlement.name if pickup_point.settlement else 'Неизвестно'
        },
        'delivery_address': delivery_address,
        'waypoints': [
            {'lat': 55.7558, 'lng': 37.6173, 'name': 'Точка 1'},
            {'lat': 55.7539, 'lng': 37.6208, 'name': 'Точка 2'}
        ]
    }


def create_trip_for_order(order_id):
    """
    Создание рейса для заказа
    
    Args:
        order_id (int): ID заказа
        
    Returns:
        dict: Результат создания рейса
    """
    order = Order.query.get(order_id)
    
    if not order:
        return {
            'success': False,
            'error': 'Заказ не найден'
        }
    
    # Получаем общий вес и объем грузов
    total_weight = sum(cargo.weight or 0 for cargo in order.cargos)
    total_volume = sum(cargo.volume or 0 for cargo in order.cargos)
    
    # Подбираем оптимальный автомобиль
    car = find_optimal_car(total_weight, total_volume)
    
    if not car:
        return {
            'success': False,
            'error': 'Не найден подходящий автомобиль'
        }
    
    # Ищем доступного водителя
    driver = find_available_driver()
    
    if not driver:
        return {
            'success': False,
            'error': 'Нет доступных водителей'
        }
    
    # Получаем пункт выдачи
    pickup_point = PickupPoint.query.get(order.pickup_point_id)
    
    if not pickup_point:
        return {
            'success': False,
            'error': 'Пункт выдачи не найден'
        }
    
    # Создаем рейс
    trip = Trip(
        driver_id=driver.id,
        car_id=car.id,
        departure_time=datetime.now() + timedelta(hours=1),
        destination=order.delivery_address
    )
    
    db.session.add(trip)
    db.session.flush()  # Чтобы получить ID рейса
    
    # Связываем грузы с рейсом
    for cargo in order.cargos:
        cargo_trip = CargoTrip(
            cargo_id=cargo.id,
            trip_id=trip.id
        )
        db.session.add(cargo_trip)
    
    # Обновляем статус заказа
    order.status = 'processing'
    
    db.session.commit()
    
    return {
        'success': True,
        'trip_id': trip.id,
        'driver': driver.full_name,
        'car': car.model,
        'departure_time': trip.departure_time.strftime('%d.%m.%Y %H:%M')
    } 