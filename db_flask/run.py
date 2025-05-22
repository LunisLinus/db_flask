#!/usr/bin/env python
import os
from dotenv import load_dotenv

from app import create_app, db
from app.models.vehicle import Car, Driver
from app.models.user import User
from app.models.order import Order, Cargo, Trip
from app.models.location import Settlement, PickupPoint

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, 
                Car=Car, 
                Driver=Driver, 
                User=User, 
                Order=Order, 
                Cargo=Cargo, 
                Trip=Trip, 
                Settlement=Settlement,
                PickupPoint=PickupPoint)

if __name__ == '__main__':
    app.run() 