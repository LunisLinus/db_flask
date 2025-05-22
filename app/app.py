#!/usr/bin/env python3
from flask import Flask
from app import db, create_app
from init_db import init_db


# Import models after app creation to avoid circular imports
def import_models():
    from app.models.user import User
    from app.models.order import Order, Cargo, PaymentMethod, Trip, CargoTrip
    from app.models.location import Settlement, PickupPoint
    from app.models.vehicle import Car, Driver
    from app.models.company import Company, InsuranceType

    return {
        'db': db,
        'User': User,
        'Order': Order,
        'Cargo': Cargo,
        'PaymentMethod': PaymentMethod,
        'Trip': Trip,
        'CargoTrip': CargoTrip,
        'Settlement': Settlement,
        'PickupPoint': PickupPoint,
        'Car': Car,
        'Driver': Driver,
        'Company': Company,
        'InsuranceType': InsuranceType,
        'init_db': init_db
    }


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return import_models()


@app.cli.command("init-db")
def initialize_db():
    """Инициализировать базу данных тестовыми данными."""
    init_db()
    print("База данных инициализирована.")


if __name__ == '__main__':
    app.run(debug=True)
