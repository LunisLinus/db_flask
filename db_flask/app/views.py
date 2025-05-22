"""
Модуль с представлениями SQL (Views) для логистической системы
"""

from sqlalchemy import text
from . import db

def create_database_views(app):
    """Создание представлений базы данных"""
    with app.app_context():
        # Представление активных заказов с клиентами и пунктами выдачи
        db.session.execute(text("""
        CREATE OR REPLACE VIEW active_orders_view AS
        SELECT 
            o.id,
            o.created_at,
            o.updated_at,
            o.status,
            o.price,
            o.delivery_address,
            o.delivery_date,
            o.notes,
            c.id as client_id,
            c.email as client_email,
            c.first_name as client_first_name,
            c.last_name as client_last_name,
            pp.id as pickup_point_id,
            pp.name as pickup_point_name,
            pp.address as pickup_point_address,
            s.name as settlement_name,
            s.region as settlement_region,
            it.type as insurance_type,
            pm.name as payment_method
        FROM orders o
        JOIN users c ON o.client_id = c.id
        LEFT JOIN pickup_points pp ON o.pickup_point_id = pp.id
        LEFT JOIN settlements s ON pp.settlement_id = s.id
        LEFT JOIN insurance_types it ON o.insurance_type_id = it.id
        LEFT JOIN payment_methods pm ON o.payment_method_id = pm.id
        WHERE o.status IN ('new', 'processing', 'delivery');
        """))
        
        # Представление для грузов с деталями заказа
        db.session.execute(text("""
        CREATE OR REPLACE VIEW cargo_details_view AS
        SELECT 
            c.id,
            c.name,
            c.weight,
            c.volume,
            c.cargo_type,
            c.package_type,
            c.order_id,
            o.status as order_status,
            o.delivery_address,
            o.created_at as order_date,
            cl.id as client_id,
            cl.email as client_email,
            cl.first_name as client_first_name,
            cl.last_name as client_last_name
        FROM cargos c
        JOIN orders o ON c.order_id = o.id
        JOIN users cl ON o.client_id = cl.id;
        """))
        
        # Представление для рейсов с водителями и автомобилями
        db.session.execute(text("""
        CREATE OR REPLACE VIEW trip_details_view AS
        SELECT 
            t.id,
            t.departure_time,
            t.arrival_time,
            t.departure_settlement_id,
            t.arrival_settlement_id,
            t.status,
            d.id as driver_id,
            CONCAT(d.first_name, ' ', d.last_name) as driver_name,
            d.phone as driver_phone,
            d.status as driver_status,
            c.id as car_id,
            c.model as car_model,
            c.license_plate as car_plate,
            c.status as car_status,
            c.capacity as car_capacity
        FROM trips t
        JOIN drivers d ON t.driver_id = d.id
        JOIN cars c ON t.car_id = c.id;
        """))
        
        # Представление для статистики по населенным пунктам
        db.session.execute(text("""
        CREATE OR REPLACE VIEW settlement_stats_view AS
        SELECT 
            s.id,
            s.name,
            s.region,
            COUNT(DISTINCT pp.id) as pickup_points_count,
            COUNT(DISTINCT o.id) as orders_count,
            SUM(o.price) as total_revenue
        FROM settlements s
        LEFT JOIN pickup_points pp ON s.id = pp.settlement_id
        LEFT JOIN orders o ON pp.id = o.pickup_point_id
        GROUP BY s.id, s.name, s.region;
        """))
        
        # Представление для статистики по водителям
        db.session.execute(text("""
        CREATE OR REPLACE VIEW driver_stats_view AS
        SELECT 
            d.id,
            CONCAT(d.first_name, ' ', d.last_name) as driver_name,
            d.status,
            COUNT(t.id) as trips_count,
            COUNT(DISTINCT c.id) as cars_used,
            COUNT(DISTINCT ct.cargo_id) as cargo_delivered
        FROM drivers d
        LEFT JOIN trips t ON d.id = t.driver_id
        LEFT JOIN cars c ON t.car_id = c.id
        LEFT JOIN cargo_trips ct ON t.id = ct.trip_id
        GROUP BY d.id, d.first_name, d.last_name, d.status;
        """))
        
        db.session.commit()


def get_orders_from_view(client_id=None, status=None):
    """
    Получить заказы из представления active_orders_view
    
    Args:
        client_id (int, optional): ID клиента для фильтрации
        status (str, optional): Статус заказа для фильтрации
        
    Returns:
        list: Список заказов из представления
    """
    query = text("SELECT * FROM active_orders_view")
    params = {}
    
    if client_id or status:
        query = text("SELECT * FROM active_orders_view WHERE 1=1")
        
        if client_id:
            query = text(f"{query.text} AND client_id = :client_id")
            params['client_id'] = client_id
            
        if status:
            query = text(f"{query.text} AND status = :status")
            params['status'] = status
    
    result = db.session.execute(query, params).fetchall()
    return result


def get_cargo_details(order_id=None):
    """
    Получить детали грузов из представления cargo_details_view
    
    Args:
        order_id (int, optional): ID заказа для фильтрации
        
    Returns:
        list: Список грузов из представления
    """
    if order_id:
        query = text("SELECT * FROM cargo_details_view WHERE order_id = :order_id")
        result = db.session.execute(query, {'order_id': order_id}).fetchall()
    else:
        query = text("SELECT * FROM cargo_details_view")
        result = db.session.execute(query).fetchall()
    
    return result


def get_trip_details(driver_id=None):
    """
    Получить детали рейсов из представления trip_details_view
    
    Args:
        driver_id (int, optional): ID водителя для фильтрации
        
    Returns:
        list: Список рейсов из представления
    """
    if driver_id:
        query = text("SELECT * FROM trip_details_view WHERE driver_id = :driver_id")
        result = db.session.execute(query, {'driver_id': driver_id}).fetchall()
    else:
        query = text("SELECT * FROM trip_details_view")
        result = db.session.execute(query).fetchall()
    
    return result


def get_settlement_stats():
    """
    Получить статистику по населенным пунктам из представления
    
    Returns:
        list: Статистика по населенным пунктам
    """
    query = text("SELECT * FROM settlement_stats_view ORDER BY orders_count DESC")
    return db.session.execute(query).fetchall()


def get_driver_stats():
    """
    Получить статистику по водителям из представления
    
    Returns:
        list: Статистика по водителям
    """
    query = text("SELECT * FROM driver_stats_view ORDER BY trips_count DESC")
    return db.session.execute(query).fetchall() 