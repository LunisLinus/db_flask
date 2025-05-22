#!/usr/bin/env python3
import sys


def init_app():
    """
    Initialize the application with data, handling app context properly
    to avoid circular imports
    """
    # Import here to avoid circular imports
    from app import create_app, db
    from app.init_db import init_db
    from flask_migrate import upgrade

    # Create app with context
    app = create_app()

    with app.app_context():
        try:
            print(">>> Запуск миграций базы данных...", file=sys.stderr)
            # Применяем все миграции, включая множественные головные ревизии
            upgrade(revision='heads')
            print(">>> Миграции успешно применены", file=sys.stderr)

            # Инициализируем данные
            print(">>> Запуск инициализации данных...", file=sys.stderr)
            init_db()
            print(">>> Инициализация завершена", file=sys.stderr)
        except Exception as e:
            print(f">>> ОШИБКА: {str(e)}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    init_app()
