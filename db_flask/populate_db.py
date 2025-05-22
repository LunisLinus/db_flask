import os
import sys
import random
import datetime
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm

# Добавляем путь к проекту в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.company import Company, InsuranceType
from app.models.location import Settlement, PickupPoint
from app.models.vehicle import Car, Driver
from app.models.order import Order, Cargo, PaymentMethod, Trip, CargoTrip

# Создаем экземпляр приложения
# Убедимся, что .env файл загружен перед созданием приложения
from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Проверяем, что DATABASE_URL правильно загружен из .env
database_url = os.environ.get('DATABASE_URL')
print(f"Используется подключение к базе данных: {database_url}")

app = create_app('development')

# Создаем экземпляр Faker для генерации данных
faker = Faker('ru_RU')

# Количество записей для каждой таблицы
NUM_RECORDS = 1000

# Размер пакета для вставки данных
BATCH_SIZE = 1000

# Списки для хранения сгенерированных ID
user_ids = []
company_ids = []
settlement_ids = []
pickup_point_ids = []
car_ids = []
driver_ids = []
payment_method_ids = []
insurance_type_ids = []
order_ids = []
cargo_ids = []
trip_ids = []

# Функция для генерации пользователей
def generate_users(count):
    print("Генерация пользователей...")
    users = []
    # Создаем множества для отслеживания уже использованных email и телефонов
    used_emails = set()
    used_phones = set()
    
    for _ in tqdm(range(count)):
        # Генерируем уникальный email
        while True:
            email = faker.email()
            # Проверяем, что такого email еще нет
            if email not in used_emails:
                used_emails.add(email)
                break
        
        # Генерируем уникальный телефон
        while True:
            phone = faker.phone_number()
            # Проверяем, что такого телефона еще нет
            if phone not in used_phones:
                used_phones.add(phone)
                break
        
        user = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=email,  # Используем уникальный email
            phone=phone,  # Используем уникальный телефон
            address=faker.address(),
            registration_date=faker.date_this_decade(),
            is_admin=random.random() < 0.05  # 5% пользователей - администраторы
        )
        user.password = faker.password(length=10)
        users.append(user)
        
        # Пакетная вставка
        if len(users) >= BATCH_SIZE:
            try:
                db.session.add_all(users)
                db.session.commit()
                # Сохраняем ID пользователей
                user_ids.extend([u.id for u in users])
                users = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении пользователей: {str(e)}")
                # Если ошибка связана с дублированием email или телефона, выводим подробную информацию
                if 'duplicate key value violates unique constraint' in str(e):
                    if 'email' in str(e):
                        print(f"Дублирующийся email: {str(e)}")
                    elif 'phone' in str(e):
                        print(f"Дублирующийся телефон: {str(e)}")
                    else:
                        print(f"Дублирующееся значение: {str(e)}")
    
    # Добавляем оставшиеся записи
    if users:
        try:
            db.session.add_all(users)
            db.session.commit()
            user_ids.extend([u.id for u in users])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении пользователей: {str(e)}")
            # Если ошибка связана с дублированием email или телефона, выводим подробную информацию
            if 'duplicate key value violates unique constraint' in str(e):
                if 'email' in str(e):
                    print(f"Дублирующийся email: {str(e)}")
                elif 'phone' in str(e):
                    print(f"Дублирующийся телефон: {str(e)}")
                else:
                    print(f"Дублирующееся значение: {str(e)}")

# Функция для генерации компаний
def generate_companies(count):
    print("Генерация компаний...")
    companies = []
    for _ in tqdm(range(count)):
        company = Company(
            name=faker.company(),
            description=faker.text(max_nb_chars=200),
            website=faker.domain_name(),
            logo_url=faker.image_url()
        )
        companies.append(company)
        
        # Пакетная вставка
        if len(companies) >= BATCH_SIZE:
            try:
                db.session.add_all(companies)
                db.session.commit()
                company_ids.extend([c.id for c in companies])
                companies = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении компаний: {str(e)}")
    
    # Добавляем оставшиеся записи
    if companies:
        try:
            db.session.add_all(companies)
            db.session.commit()
            company_ids.extend([c.id for c in companies])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении компаний: {str(e)}")

# Функция для генерации типов страховок
def generate_insurance_types(count):
    print("Генерация типов страховок...")
    insurance_types = []
    for _ in tqdm(range(count)):
        if not company_ids:
            print("Нет доступных компаний для создания типов страховок")
            break
            
        insurance_type = InsuranceType(
            company_id=random.choice(company_ids),
            type=random.choice(["Базовая", "Стандартная", "Премиум", "VIP", "Полная"]),
            description=faker.text(max_nb_chars=150),
            price=round(random.uniform(500, 10000), 2)
        )
        insurance_types.append(insurance_type)
        
        # Пакетная вставка
        if len(insurance_types) >= BATCH_SIZE:
            try:
                db.session.add_all(insurance_types)
                db.session.commit()
                insurance_type_ids.extend([i.id for i in insurance_types])
                insurance_types = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении типов страховок: {str(e)}")
    
    # Добавляем оставшиеся записи
    if insurance_types:
        try:
            db.session.add_all(insurance_types)
            db.session.commit()
            insurance_type_ids.extend([i.id for i in insurance_types])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении типов страховок: {str(e)}")

# Функция для генерации населенных пунктов
def generate_settlements(count):
    print("Генерация населенных пунктов...")
    settlements = []
    for _ in tqdm(range(count)):
        settlement = Settlement(
            name=faker.city(),
            region=faker.region(),
            country="Россия",
            postal_code=faker.postcode()
        )
        settlements.append(settlement)
        
        # Пакетная вставка
        if len(settlements) >= BATCH_SIZE:
            try:
                db.session.add_all(settlements)
                db.session.commit()
                settlement_ids.extend([s.id for s in settlements])
                settlements = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении населенных пунктов: {str(e)}")
    
    # Добавляем оставшиеся записи
    if settlements:
        try:
            db.session.add_all(settlements)
            db.session.commit()
            settlement_ids.extend([s.id for s in settlements])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении населенных пунктов: {str(e)}")

# Функция для генерации пунктов выдачи
def generate_pickup_points(count):
    print("Генерация пунктов выдачи...")
    
    # Создаем множество для отслеживания уже использованных телефонов
    used_phones = set()
    
    pickup_points = []
    for _ in tqdm(range(count)):
        if not settlement_ids:
            print("Нет доступных населенных пунктов для создания пунктов выдачи")
            break
        
        # Генерируем уникальный телефон
        while True:
            phone = faker.phone_number()
            # Проверяем, что такого телефона еще нет
            if phone not in used_phones:
                used_phones.add(phone)
                break
            
        pickup_point = PickupPoint(
            name=f"Пункт выдачи {faker.word()}",
            address=faker.street_address(),
            settlement_id=random.choice(settlement_ids),
            phone=phone,  # Используем уникальный телефон
            working_hours=f"{random.randint(8, 10)}:00 - {random.randint(18, 22)}:00",
            is_active=random.random() < 0.9  # 90% пунктов активны
        )
        pickup_points.append(pickup_point)
        
        # Пакетная вставка
        if len(pickup_points) >= BATCH_SIZE:
            try:
                db.session.add_all(pickup_points)
                db.session.commit()
                pickup_point_ids.extend([p.id for p in pickup_points])
                pickup_points = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении пунктов выдачи: {str(e)}")
                # Если ошибка связана с дублированием телефона, выводим подробную информацию
                if 'duplicate key value violates unique constraint' in str(e):
                    print(f"Дублирующийся телефон: {str(e)}")
    
    # Добавляем оставшиеся записи
    if pickup_points:
        try:
            db.session.add_all(pickup_points)
            db.session.commit()
            pickup_point_ids.extend([p.id for p in pickup_points])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении пунктов выдачи: {str(e)}")
            # Если ошибка связана с дублированием телефона, выводим подробную информацию
            if 'duplicate key value violates unique constraint' in str(e):
                print(f"Дублирующийся телефон: {str(e)}")

# Функция для генерации автомобилей
def generate_cars(count):
    print("Генерация автомобилей...")
    car_brands = ["Газель", "Камаз", "МАЗ", "Volvo", "Mercedes", "Scania", "MAN", "Iveco", "DAF", "Renault"]
    car_models = ["Next", "FH16", "Actros", "R450", "TGX", "Stralis", "XF", "T-Series", "65115", "5440"]
    car_statuses = ["available", "in_use", "maintenance"]
    
    # Создаем множество для отслеживания уже использованных номеров
    used_license_plates = set()
    
    cars = []
    for _ in tqdm(range(count)):
        brand = random.choice(car_brands)
        model = random.choice(car_models)
        
        # Генерируем уникальный номерной знак
        while True:
            license_plate = f"{random.choice('АВЕКМНОРСТУХ')}{random.randint(100, 999)}{random.choice('АВЕКМНОРСТУХ')}{random.choice('АВЕКМНОРСТУХ')} {random.randint(10, 199)}"
            # Проверяем, что такого номера еще нет
            if license_plate not in used_license_plates:
                used_license_plates.add(license_plate)
                break
        
        car = Car(
            brand=brand,
            model=model,
            license_plate=license_plate,
            year=random.randint(2010, 2023),
            capacity=round(random.uniform(1.5, 20.0), 1),  # тонны
            volume=round(random.uniform(10.0, 100.0), 1),  # м³
            status=random.choices(car_statuses, weights=[0.7, 0.2, 0.1])[0]
        )
        cars.append(car)
        
        # Пакетная вставка
        if len(cars) >= BATCH_SIZE:
            try:
                db.session.add_all(cars)
                db.session.commit()
                car_ids.extend([c.id for c in cars])
                cars = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении автомобилей: {str(e)}")
                # Если ошибка связана с дублированием номера, выводим подробную информацию
                if 'duplicate key value violates unique constraint' in str(e):
                    print(f"Дублирующийся номерной знак: {str(e)}")
    
    # Добавляем оставшиеся записи
    if cars:
        try:
            db.session.add_all(cars)
            db.session.commit()
            car_ids.extend([c.id for c in cars])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении автомобилей: {str(e)}")
            # Если ошибка связана с дублированием номера, выводим подробную информацию
            if 'duplicate key value violates unique constraint' in str(e):
                print(f"Дублирующийся номерной знак: {str(e)}")

# Функция для генерации водителей
def generate_drivers(count):
    print("Генерация водителей...")
    driver_statuses = ["available", "busy", "off"]
    
    # Создаем множества для отслеживания уже использованных email и телефонов
    used_emails = set()
    used_phones = set()
    used_license_numbers = set()
    
    drivers = []
    for _ in tqdm(range(count)):
        # Генерируем уникальный email
        while True:
            email = faker.email()
            # Проверяем, что такого email еще нет
            if email not in used_emails:
                used_emails.add(email)
                break
        
        # Генерируем уникальный телефон
        while True:
            phone = faker.phone_number()
            # Проверяем, что такого телефона еще нет
            if phone not in used_phones:
                used_phones.add(phone)
                break
        
        # Генерируем уникальный номер лицензии
        while True:
            license_number = f"{random.randint(10, 99)} {random.randint(10, 99)} {random.randint(100000, 999999)}"
            # Проверяем, что такого номера лицензии еще нет
            if license_number not in used_license_numbers:
                used_license_numbers.add(license_number)
                break
                
        driver = Driver(
            first_name=faker.first_name_male(),
            last_name=faker.last_name_male(),
            license_number=license_number,
            phone=phone,  # Используем уникальный телефон
            email=email,  # Используем уникальный email
            status=random.choices(driver_statuses, weights=[0.6, 0.3, 0.1])[0],
            car_id=random.choice(car_ids) if car_ids else None
        )
        drivers.append(driver)
        
        # Пакетная вставка
        if len(drivers) >= BATCH_SIZE:
            try:
                db.session.add_all(drivers)
                db.session.commit()
                driver_ids.extend([d.id for d in drivers])
                drivers = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении водителей: {str(e)}")
                # Если ошибка связана с дублированием email, телефона или номера лицензии, выводим подробную информацию
                if 'duplicate key value violates unique constraint' in str(e):
                    if 'email' in str(e):
                        print(f"Дублирующийся email: {str(e)}")
                    elif 'phone' in str(e):
                        print(f"Дублирующийся телефон: {str(e)}")
                    elif 'license_number' in str(e):
                        print(f"Дублирующийся номер лицензии: {str(e)}")
                    else:
                        print(f"Дублирующееся значение: {str(e)}")
    
    # Добавляем оставшиеся записи
    if drivers:
        try:
            db.session.add_all(drivers)
            db.session.commit()
            driver_ids.extend([d.id for d in drivers])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении водителей: {str(e)}")
            # Если ошибка связана с дублированием email, телефона или номера лицензии, выводим подробную информацию
            if 'duplicate key value violates unique constraint' in str(e):
                if 'email' in str(e):
                    print(f"Дублирующийся email: {str(e)}")
                elif 'phone' in str(e):
                    print(f"Дублирующийся телефон: {str(e)}")
                elif 'license_number' in str(e):
                    print(f"Дублирующийся номер лицензии: {str(e)}")
                else:
                    print(f"Дублирующееся значение: {str(e)}")

# Функция для генерации способов оплаты
def generate_payment_methods(count):
    print("Генерация способов оплаты...")
    payment_method_names = [
        "Наличные", "Банковская карта", "Онлайн-оплата", "Счет на юридическое лицо", 
        "Электронный кошелек", "Криптовалюта", "Рассрочка", "Кредит", "Подарочная карта"
    ]
    
    # Создаем множество для отслеживания уже использованных имен
    used_names = set(payment_method_names)
    
    payment_methods = []
    for name in payment_method_names:
        payment_method = PaymentMethod(
            name=name,
            description=faker.text(max_nb_chars=100),
            is_active=True
        )
        payment_methods.append(payment_method)
    
    # Добавляем все способы оплаты
    try:
        db.session.add_all(payment_methods)
        db.session.commit()
        payment_method_ids.extend([p.id for p in payment_methods])
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Ошибка при добавлении способов оплаты: {str(e)}")
        # Если ошибка связана с дублированием имени, выводим подробную информацию
        if 'duplicate key value violates unique constraint' in str(e):
            print(f"Дублирующееся имя способа оплаты: {str(e)}")
    
    # Генерируем дополнительные записи, если нужно
    if count > len(payment_method_names):
        additional_count = count - len(payment_method_names)
        payment_methods = []
        
        for _ in tqdm(range(additional_count)):
            # Генерируем уникальное имя
            while True:
                name = f"Способ оплаты {faker.word()}"
                # Проверяем, что такого имени еще нет
                if name not in used_names:
                    used_names.add(name)
                    break
            
            payment_method = PaymentMethod(
                name=name,
                description=faker.text(max_nb_chars=100),
                is_active=random.random() < 0.8  # 80% способов активны
            )
            payment_methods.append(payment_method)
            
            # Пакетная вставка
            if len(payment_methods) >= BATCH_SIZE:
                try:
                    db.session.add_all(payment_methods)
                    db.session.commit()
                    payment_method_ids.extend([p.id for p in payment_methods])
                    payment_methods = []
                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"Ошибка при добавлении способов оплаты: {str(e)}")
                    # Если ошибка связана с дублированием имени, выводим подробную информацию
                    if 'duplicate key value violates unique constraint' in str(e):
                        print(f"Дублирующееся имя способа оплаты: {str(e)}")
        
        # Добавляем оставшиеся записи
        if payment_methods:
            try:
                db.session.add_all(payment_methods)
                db.session.commit()
                payment_method_ids.extend([p.id for p in payment_methods])
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении способов оплаты: {str(e)}")
                # Если ошибка связана с дублированием имени, выводим подробную информацию
                if 'duplicate key value violates unique constraint' in str(e):
                    print(f"Дублирующееся имя способа оплаты: {str(e)}")

# Функция для генерации заказов
def generate_orders(count):
    print("Генерация заказов...")
    order_statuses = ["new", "in_progress", "completed", "cancelled"]
    
    orders = []
    for _ in tqdm(range(count)):
        if not user_ids or not pickup_point_ids:
            print("Нет доступных пользователей или пунктов выдачи для создания заказов")
            break
            
        created_date = faker.date_time_this_year()
        delivery_date = created_date + datetime.timedelta(days=random.randint(1, 30))
        
        order = Order(
            client_id=random.choice(user_ids),
            payment_method_id=random.choice(payment_method_ids) if payment_method_ids else None,
            insurance_type_id=random.choice(insurance_type_ids) if insurance_type_ids and random.random() < 0.7 else None,
            pickup_point_id=random.choice(pickup_point_ids),
            status=random.choices(order_statuses, weights=[0.3, 0.3, 0.3, 0.1])[0],
            price=round(random.uniform(1000, 50000), 2),
            created_at=created_date,
            updated_at=created_date,
            delivery_address=faker.address(),
            delivery_date=delivery_date.date(),
            notes=faker.text(max_nb_chars=100) if random.random() < 0.5 else None
        )
        orders.append(order)
        
        # Пакетная вставка
        if len(orders) >= BATCH_SIZE:
            try:
                db.session.add_all(orders)
                db.session.commit()
                order_ids.extend([o.id for o in orders])
                orders = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении заказов: {str(e)}")
    
    # Добавляем оставшиеся записи
    if orders:
        try:
            db.session.add_all(orders)
            db.session.commit()
            order_ids.extend([o.id for o in orders])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении заказов: {str(e)}")

# Функция для генерации грузов
def generate_cargos(count):
    print("Генерация грузов...")
    cargo_types = ["Бытовая техника", "Мебель", "Одежда", "Продукты", "Стройматериалы", "Электроника", "Документы", "Хрупкие предметы"]
    package_types = ["Коробка", "Паллет", "Контейнер", "Мешок", "Ящик", "Бочка", "Без упаковки"]
    
    cargos = []
    for _ in tqdm(range(count)):
        if not order_ids:
            print("Нет доступных заказов для создания грузов")
            break
            
        cargo = Cargo(
            name=f"{faker.word().capitalize()} {faker.word()}",
            weight=round(random.uniform(0.1, 1000.0), 2),
            volume=round(random.uniform(0.01, 100.0), 2),
            order_id=random.choice(order_ids),
            cargo_type=random.choice(cargo_types),
            package_type=random.choice(package_types)
        )
        cargos.append(cargo)
        
        # Пакетная вставка
        if len(cargos) >= BATCH_SIZE:
            try:
                db.session.add_all(cargos)
                db.session.commit()
                cargo_ids.extend([c.id for c in cargos])
                cargos = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении грузов: {str(e)}")
    
    # Добавляем оставшиеся записи
    if cargos:
        try:
            db.session.add_all(cargos)
            db.session.commit()
            cargo_ids.extend([c.id for c in cargos])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении грузов: {str(e)}")

# Функция для генерации рейсов
def generate_trips(count):
    print("Генерация рейсов...")
    trip_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
    
    trips = []
    for _ in tqdm(range(count)):
        if not settlement_ids or not driver_ids or not car_ids:
            print("Нет доступных населенных пунктов, водителей или автомобилей для создания рейсов")
            break
            
        # Выбираем два разных населенных пункта
        departure_settlement_id = random.choice(settlement_ids)
        arrival_settlement_id = random.choice([s for s in settlement_ids if s != departure_settlement_id])
        
        departure_time = faker.date_time_this_year()
        arrival_time = departure_time + datetime.timedelta(hours=random.randint(1, 72))
        
        trip = Trip(
            departure_time=departure_time,
            arrival_time=arrival_time if random.random() < 0.8 else None,  # 20% рейсов без времени прибытия
            departure_settlement_id=departure_settlement_id,
            arrival_settlement_id=arrival_settlement_id,
            driver_id=random.choice(driver_ids),
            car_id=random.choice(car_ids),
            status=random.choices(trip_statuses, weights=[0.3, 0.3, 0.3, 0.1])[0]
        )
        trips.append(trip)
        
        # Пакетная вставка
        if len(trips) >= BATCH_SIZE:
            try:
                db.session.add_all(trips)
                db.session.commit()
                trip_ids.extend([t.id for t in trips])
                trips = []
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при добавлении рейсов: {str(e)}")
    
    # Добавляем оставшиеся записи
    if trips:
        try:
            db.session.add_all(trips)
            db.session.commit()
            trip_ids.extend([t.id for t in trips])
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении рейсов: {str(e)}")

# Функция для генерации связей между грузами и рейсами
def generate_cargo_trips(count):
    print("Генерация связей между грузами и рейсами...")
    cargo_trips = []
    
    # Создаем уникальные пары груз-рейс
    cargo_trip_pairs = set()
    
    # Ограничиваем количество попыток для предотвращения бесконечного цикла
    max_attempts = count * 2
    attempts = 0
    successful_pairs = 0
    
    while successful_pairs < count and attempts < max_attempts:
        attempts += 1
        
        if not cargo_ids or not trip_ids:
            print("Нет доступных грузов или рейсов для создания связей")
            break
            
        cargo_id = random.choice(cargo_ids)
        trip_id = random.choice(trip_ids)
        
        # Проверяем, что такой пары еще нет
        if (cargo_id, trip_id) not in cargo_trip_pairs:
            cargo_trip_pairs.add((cargo_id, trip_id))
            successful_pairs += 1
            
            cargo_trip = CargoTrip(
                cargo_id=cargo_id,
                trip_id=trip_id
            )
            cargo_trips.append(cargo_trip)
            
            # Пакетная вставка
            if len(cargo_trips) >= BATCH_SIZE:
                try:
                    db.session.add_all(cargo_trips)
                    db.session.commit()
                    cargo_trips = []
                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(f"Ошибка при добавлении связей груз-рейс: {str(e)}")
                    # Если ошибка связана с дублированием пары, выводим подробную информацию
                    if 'duplicate key value violates unique constraint' in str(e):
                        print(f"Дублирующаяся пара груз-рейс: {str(e)}")
    
    # Добавляем оставшиеся записи
    if cargo_trips:
        try:
            db.session.add_all(cargo_trips)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Ошибка при добавлении связей груз-рейс: {str(e)}")
            # Если ошибка связана с дублированием пары, выводим подробную информацию
            if 'duplicate key value violates unique constraint' in str(e):
                print(f"Дублирующаяся пара груз-рейс: {str(e)}")
    
    print(f"Создано {successful_pairs} уникальных пар груз-рейс из {attempts} попыток")

# Основная функция для заполнения базы данных
def populate_database():
    with app.app_context():
        print("Начало заполнения базы данных...")
        
        # Проверяем соединение с базой данных
        try:
            # Проверяем, есть ли уже данные в базе
            user_count = db.session.query(User).count()
            if user_count > 0:
                print(f"В базе данных уже есть {user_count} пользователей.")
                proceed = input("Продолжить заполнение базы данных? (y/n): ")
                if proceed.lower() != 'y':
                    print("Заполнение базы данных отменено.")
                    return
            
            # Генерируем данные для каждой таблицы в транзакции
            db.session.begin_nested()  # Создаем точку сохранения

            generate_orders(NUM_RECORDS)
            generate_cargos(NUM_RECORDS)
            generate_trips(NUM_RECORDS)
            generate_cargo_trips(NUM_RECORDS)
            
            print("База данных успешно заполнена!")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Произошла ошибка при заполнении базы данных: {str(e)}")
        except Exception as e:
            db.session.rollback()
            print(f"Непредвиденная ошибка: {str(e)}")
        finally:
            db.session.close()

if __name__ == "__main__":
    populate_database()