#!/usr/bin/env python3
"""
Скрипт для объединения нескольких головных ревизий миграции базы данных.
Запустите этот скрипт, если у вас появляется ошибка 'Multiple head revisions'.
"""
import os
import sys
from flask_migrate import Migrate, stamp
from flask import Flask
from app import db, create_app


def merge_migration_heads():
    """Объединяет несколько головных ревизий миграции."""
    print("Запуск объединения головных ревизий миграции...")

    app = create_app()

    with app.app_context():
        # Получаем текущие миграции и печатаем их для информации
        from flask_migrate import current
        revisions = current(verbose=True)

        try:
            # Запускаем команду alembic для объединения ревизий
            os.system('cd {} && python -m flask db merge heads -m "merge_multiple_heads"'.format(os.getcwd()))
            print("Ревизии объединены. Теперь запустите 'flask db upgrade' для применения миграций.")
        except Exception as e:
            print(f"Ошибка при объединении ревизий: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    merge_migration_heads()
