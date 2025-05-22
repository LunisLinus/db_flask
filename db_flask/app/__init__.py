from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
mail = Mail()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .orders import orders as orders_blueprint
    app.register_blueprint(orders_blueprint, url_prefix='/orders')

    from .reports import reports as reports_blueprint
    app.register_blueprint(reports_blueprint, url_prefix='/reports')
    
    # Инициализируем базу данных сразу при создании приложения
    with app.app_context():
        try:
            # Register SQL functions and procedures
            from .procedures import register_sql_functions
            register_sql_functions(app)
            
            # Create SQL views
            from .views import create_database_views
            create_database_views(app)
            
            app.logger.info("SQL functions, procedures and views registered successfully")
        except Exception as e:
            app.logger.error(f"Error initializing database functions: {str(e)}")

    return app 