from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sys
from .. import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    registration_date = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='client', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        print(f">>> Setting password hash for user {self.email}", file=sys.stderr)
        self.password_hash = generate_password_hash(password)
        print(f">>> Password hash set to: {self.password_hash}", file=sys.stderr)

    def verify_password(self, password):
        print(f">>> Verifying password for user {self.email}", file=sys.stderr)
        print(f">>> Stored hash: {self.password_hash}", file=sys.stderr)
        result = check_password_hash(self.password_hash, password)
        print(f">>> Password verification result: {result}", file=sys.stderr)
        return result

    def is_admin_user(self):
        return self.is_admin

    @staticmethod
    @login_manager.user_loader
    def load_user(user_id):
        print(f">>> Loading user with ID: {user_id}", file=sys.stderr)
        user = User.query.get(int(user_id))
        print(f">>> User loaded: {user}", file=sys.stderr)
        return user

    def __repr__(self):
        return f'<User {self.email}>' 