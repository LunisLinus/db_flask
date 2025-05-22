import random
from faker import Faker
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    Company, InsuranceType, Settlement, PickupPoint, Order, Cargo, PaymentMethod, Trip,
    CargoTrip, User, Car, Driver
)

fake = Faker('ru_RU')
app = create_app()
BATCH_SIZE = 5000  # Bulk insert chunk size


def bulk_insert(model, objects):
    for i in range(0, len(objects), BATCH_SIZE):
        db.session.bulk_save_objects(objects[i:i + BATCH_SIZE])
        db.session.commit()


def generate_companies(n=100_000):
    companies = []
    for i in range(n):
        companies.append(Company(
            name=fake.unique.company()[:250],
            description=fake.text(max_nb_chars=200),
            logo_url=fake.image_url(),
            website=fake.url(),
            created_at=fake.date_time_this_decade()
        ))
    bulk_insert(Company, companies)
    return Company.query.with_entities(Company.id).all()


def generate_insurance_types(company_ids, n=100_000):
    insurance_types = []
    for i in range(n):
        insurance_types.append(InsuranceType(
            company_id=random.choice(company_ids)[0],
            type=fake.unique.word() + f" {i}",
            description=fake.text(max_nb_chars=100),
            price=round(random.uniform(1000, 10000), 2),
            created_at=fake.date_time_this_decade()
        ))
    bulk_insert(InsuranceType, insurance_types)
    return InsuranceType.query.with_entities(InsuranceType.id).all()


def generate_settlements(n=100_000):
    settlements = []
    for i in range(n):
        settlements.append(Settlement(
            name=fake.unique.city()[:99],
            region=fake.region(),
            country='Россия',
            postal_code=fake.postcode()
        ))
    bulk_insert(Settlement, settlements)
    return Settlement.query.with_entities(Settlement.id).all()


def generate_pickup_points(settlement_ids, n=100_000):
    pickup_points = []
    for i in range(n):
        pickup_points.append(PickupPoint(
            name=f"ПВЗ {fake.unique.word()}_{i}",
            address=fake.street_address(),
            settlement_id=random.choice(settlement_ids)[0],
            phone=fake.phone_number(),
            working_hours="09:00-21:00",
            is_active=True
        ))
    bulk_insert(PickupPoint, pickup_points)
    return PickupPoint.query.with_entities(PickupPoint.id).all()


def generate_payment_methods(n=20):
    payment_methods = []
    for i in range(n):
        payment_methods.append(PaymentMethod(
            name=fake.unique.word() + f" method {i}",
            description=fake.text(max_nb_chars=50),
            is_active=True,
            created_at=fake.date_time_this_decade()
        ))
    bulk_insert(PaymentMethod, payment_methods)
    return PaymentMethod.query.with_entities(PaymentMethod.id).all()


def generate_users(n=100_000):
    users = []
    for i in range(n):
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            address=fake.address(),
            registration_date=fake.date_between(start_date='-5y', end_date='today'),
            is_admin=(i % 10 == 0),
            created_at=fake.date_time_this_decade()
        )
        user.password = "password"  # Используйте сеттер для password_hash!
        users.append(user)
    bulk_insert(User, users)
    return User.query.with_entities(User.id).all()


def generate_orders(user_ids, payment_method_ids, insurance_type_ids, pickup_point_ids, n=100_000):
    orders = []
    statuses = ['new', 'in_progress', 'completed', 'cancelled']
    for i in range(n):
        orders.append(Order(
            client_id=random.choice(user_ids)[0],
            payment_method_id=random.choice(payment_method_ids)[0],
            insurance_type_id=random.choice(insurance_type_ids)[0],
            pickup_point_id=random.choice(pickup_point_ids)[0],
            status=random.choice(statuses),
            price=round(random.uniform(500, 20000), 2),
            created_at=fake.date_time_this_year(),
            updated_at=fake.date_time_this_year(),
            delivery_address=fake.address(),
            delivery_date=fake.date_between(start_date='today', end_date='+30d'),
            notes=fake.sentence()
        ))
    bulk_insert(Order, orders)
    return Order.query.with_entities(Order.id).all()


def generate_cargos(order_ids, n=100_000):
    cargos = []
    cargo_types = ["груз", "документы", "мебель", "техника"]
    package_types = ["коробка", "пакет", "паллет", "контейнер"]
    for i in range(n):
        cargos.append(Cargo(
            name=fake.unique.word() + f" cargo {i}",
            weight=round(random.uniform(0.1, 1000), 2),
            volume=round(random.uniform(0.01, 15), 2),
            order_id=random.choice(order_ids)[0],
            cargo_type=random.choice(cargo_types),
            package_type=random.choice(package_types)
        ))
    bulk_insert(Cargo, cargos)
    return Cargo.query.with_entities(Cargo.id).all()


def generate_cars(n=100_000):
    cars = []
    statuses = ["available", "in_use", "maintenance"]
    for i in range(n):
        cars.append(Car(
            brand=fake.company()[:49],
            model=fake.word()[:49],
            license_plate=f"Р{random.randint(100, 999)}{fake.unique.lexify(text='???')}77",
            year=random.randint(2000, 2024),
            capacity=round(random.uniform(0.5, 20), 2),
            volume=round(random.uniform(2, 100), 2),
            status=random.choice(statuses),
            created_at=fake.date_time_this_decade()
        ))
    bulk_insert(Car, cars)
    return Car.query.with_entities(Car.id).all()


def generate_drivers(car_ids, n=100_000):
    drivers = []
    statuses = ["available", "busy", "off"]
    for i in range(n):
        drivers.append(Driver(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            license_number=fake.unique.bothify(text='??####77'),
            phone=fake.phone_number(),
            email=fake.unique.email(),
            status=random.choice(statuses),
            car_id=random.choice(car_ids)[0],
            created_at=fake.date_time_this_decade()
        ))
    bulk_insert(Driver, drivers)
    return Driver.query.with_entities(Driver.id).all()


def generate_trips(settlement_ids, driver_ids, car_ids, n=100_000):
    trips = []
    statuses = ["scheduled", "in_progress", "completed", "cancelled"]
    for i in range(n):
        dep, arr = random.sample(settlement_ids, 2)
        departure_time = fake.date_time_this_year()
        arrival_time = departure_time + timedelta(hours=random.randint(2, 24))
        trips.append(Trip(
            departure_time=departure_time,
            arrival_time=arrival_time,
            departure_settlement_id=dep[0],
            arrival_settlement_id=arr[0],
            driver_id=random.choice(driver_ids)[0],
            car_id=random.choice(car_ids)[0],
            status=random.choice(statuses)
        ))
    bulk_insert(Trip, trips)
    return Trip.query.with_entities(Trip.id).all()


def generate_cargo_trips(cargo_ids, trip_ids, n=100_000):
    cargo_trips = []
    used = set()
    for i in range(n):
        cargo_id = random.choice(cargo_ids)[0]
        trip_id = random.choice(trip_ids)[0]
        # Гарантия уникальной связки (cargo_id, trip_id)
        if (cargo_id, trip_id) in used:
            continue
        used.add((cargo_id, trip_id))
        cargo_trips.append(CargoTrip(
            cargo_id=cargo_id,
            trip_id=trip_id
        ))
    bulk_insert(CargoTrip, cargo_trips)


def main():
    with app.app_context():
        print('Generating companies...')
        company_ids = generate_companies()
        print('Generating insurance types...')
        insurance_type_ids = generate_insurance_types(company_ids)
        print('Generating settlements...')
        settlement_ids = generate_settlements()
        print('Generating pickup points...')
        pickup_point_ids = generate_pickup_points(settlement_ids)
        print('Generating payment methods...')
        payment_method_ids = generate_payment_methods()
        print('Generating users...')
        user_ids = generate_users()
        print('Generating orders...')
        order_ids = generate_orders(user_ids, payment_method_ids, insurance_type_ids, pickup_point_ids)
        print('Generating cargos...')
        cargo_ids = generate_cargos(order_ids)
        print('Generating cars...')
        car_ids = generate_cars()
        print('Generating drivers...')
        driver_ids = generate_drivers(car_ids)
        print('Generating trips...')
        trip_ids = generate_trips(settlement_ids, driver_ids, car_ids)
        print('Generating cargo_trips...')
        generate_cargo_trips(cargo_ids, trip_ids)
        print('Done!')


if __name__ == "__main__":
    main()
