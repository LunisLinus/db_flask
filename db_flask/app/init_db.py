from app import db, create_app
from app.models.order import PaymentMethod
from app.models.company import InsuranceType, Company
from app.models.location import Settlement, PickupPoint
import sys
from sqlalchemy import text

def init_payment_methods():
    """Инициализация способов оплаты"""
    # Проверяем, есть ли уже данные
    if PaymentMethod.query.count() == 0:
        payment_methods = [
            {'name': 'Наличные при получении', 'description': 'Оплата наличными при получении заказа'},
            {'name': 'Банковская карта при получении', 'description': 'Оплата картой при получении заказа'},
            {'name': 'Банковский перевод', 'description': 'Оплата через банковский перевод'},
            {'name': 'Онлайн-оплата', 'description': 'Оплата через онлайн-платежную систему'},
            {'name': 'Криптовалюта', 'description': 'Оплата криптовалютой'}
        ]
        
        for method_data in payment_methods:
            method = PaymentMethod(
                name=method_data['name'],
                description=method_data['description'],
                is_active=True
            )
            db.session.add(method)
        
        db.session.commit()
        print(f"Добавлено {len(payment_methods)} способов оплаты", file=sys.stderr)
    else:
        print("Способы оплаты уже существуют в базе данных", file=sys.stderr)

def init_insurance_types():
    """Инициализация типов страховки"""
    # Проверяем, есть ли уже данные
    if InsuranceType.query.count() == 0:
        # Создаем тестовую компанию для страховок если её нет
        company = Company.query.first()
        if not company:
            company = Company(
                name='Страховая компания "Безопасность"',
                description='Тестовая компания для системы логистики',
                website='https://example.com'
            )
            db.session.add(company)
            db.session.commit()
            print("Создана тестовая страховая компания", file=sys.stderr)
        
        insurance_types = [
            {'type': 'Базовая страховка', 'description': 'Базовое страхование груза', 'price': 500.0},
            {'type': 'Стандартная страховка', 'description': 'Стандартное страхование с расширенным покрытием', 'price': 1000.0},
            {'type': 'Премиум страховка', 'description': 'Полное страхование от всех рисков', 'price': 2000.0}
        ]
        
        for insurance_data in insurance_types:
            insurance = InsuranceType(
                type=insurance_data['type'],
                description=insurance_data['description'],
                price=insurance_data['price'],
                company_id=company.id
            )
            db.session.add(insurance)
        
        db.session.commit()
        print(f"Добавлено {len(insurance_types)} типов страховки", file=sys.stderr)
    else:
        print("Типы страховки уже существуют в базе данных", file=sys.stderr)

def init_settlements():
    """Инициализация населенных пунктов"""
    # Проверяем, есть ли уже данные
    if Settlement.query.count() == 0:
        settlements = [
            {'name': 'Москва', 'region': 'Московская область', 'country': 'Россия', 'postal_code': '101000'},
            {'name': 'Санкт-Петербург', 'region': 'Ленинградская область', 'country': 'Россия', 'postal_code': '190000'},
            {'name': 'Новосибирск', 'region': 'Новосибирская область', 'country': 'Россия', 'postal_code': '630000'},
            {'name': 'Екатеринбург', 'region': 'Свердловская область', 'country': 'Россия', 'postal_code': '620000'},
            {'name': 'Казань', 'region': 'Республика Татарстан', 'country': 'Россия', 'postal_code': '420000'}
        ]
        
        for settlement_data in settlements:
            settlement = Settlement(
                name=settlement_data['name'],
                region=settlement_data['region'],
                country=settlement_data['country'],
                postal_code=settlement_data['postal_code']
            )
            db.session.add(settlement)
        
        db.session.commit()
        print(f"Добавлено {len(settlements)} населенных пунктов", file=sys.stderr)
    else:
        print("Населенные пункты уже существуют в базе данных", file=sys.stderr)
    
    return Settlement.query.all()

def init_pickup_points(settlements):
    """Инициализация пунктов выдачи"""
    # Проверяем, есть ли уже данные
    if PickupPoint.query.count() == 0:
        pickup_points = [
            # Москва
            {'name': 'Пункт выдачи Центральный', 'address': 'ул. Тверская, 15', 'settlement_id': 1, 
             'phone': '+7 (495) 123-45-67', 'working_hours': 'Пн-Пт: 9:00-20:00, Сб-Вс: 10:00-18:00'},
            {'name': 'Пункт выдачи Южный', 'address': 'Каширское шоссе, 25', 'settlement_id': 1, 
             'phone': '+7 (495) 234-56-78', 'working_hours': 'Пн-Вс: 9:00-21:00'},
            # Санкт-Петербург
            {'name': 'Пункт выдачи на Невском', 'address': 'Невский проспект, 45', 'settlement_id': 2, 
             'phone': '+7 (812) 345-67-89', 'working_hours': 'Пн-Пт: 10:00-21:00, Сб-Вс: 11:00-19:00'},
            {'name': 'Пункт выдачи Васильевский', 'address': 'Васильевский остров, 7-я линия, 30', 'settlement_id': 2, 
             'phone': '+7 (812) 456-78-90', 'working_hours': 'Пн-Вс: 10:00-20:00'},
            # Новосибирск
            {'name': 'Пункт выдачи Центральный', 'address': 'ул. Ленина, 10', 'settlement_id': 3, 
             'phone': '+7 (383) 567-89-01', 'working_hours': 'Пн-Пт: 9:00-19:00, Сб: 10:00-16:00, Вс: выходной'},
            # Екатеринбург
            {'name': 'Пункт выдачи Уральский', 'address': 'ул. Малышева, 25', 'settlement_id': 4, 
             'phone': '+7 (343) 678-90-12', 'working_hours': 'Пн-Вс: 9:00-20:00'},
            # Казань
            {'name': 'Пункт выдачи Кремлевский', 'address': 'ул. Баумана, 15', 'settlement_id': 5, 
             'phone': '+7 (843) 789-01-23', 'working_hours': 'Пн-Сб: 9:00-20:00, Вс: 10:00-18:00'}
        ]
        
        for point_data in pickup_points:
            # Если передан массив settlements, используем id из него
            if settlements and point_data['settlement_id'] <= len(settlements):
                settlement_id = settlements[point_data['settlement_id'] - 1].id
            else:
                settlement_id = point_data['settlement_id']
                
            point = PickupPoint(
                name=point_data['name'],
                address=point_data['address'],
                settlement_id=settlement_id,
                phone=point_data['phone'],
                working_hours=point_data['working_hours'],
                is_active=True
            )
            db.session.add(point)
        
        db.session.commit()
        print(f"Добавлено {len(pickup_points)} пунктов выдачи", file=sys.stderr)
    else:
        print("Пункты выдачи уже существуют в базе данных", file=sys.stderr)

def init_db():
    """Инициализация всех данных в базе данных"""
    print(">>> Начинаем инициализацию базы данных...", file=sys.stderr)
    
    # Создаем экземпляр приложения и контекст приложения
    app = create_app()
    with app.app_context():
        try:
            # Проверяем соединение с базой
            print(">>> Проверка соединения с базой данных...", file=sys.stderr)
            db.session.execute(text("SELECT 1"))
            
            print(">>> Инициализация способов оплаты...", file=sys.stderr)
            init_payment_methods()
            
            print(">>> Инициализация типов страховки...", file=sys.stderr)
            init_insurance_types()
            
            print(">>> Инициализация населенных пунктов...", file=sys.stderr)
            settlements = init_settlements()
            
            print(">>> Инициализация пунктов выдачи...", file=sys.stderr)
            init_pickup_points(settlements)
            
            print(">>> Инициализация базы данных завершена успешно!", file=sys.stderr)
        except Exception as e:
            print(f">>> ОШИБКА при инициализации базы данных: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)

if __name__ == "__main__":
    init_db() 