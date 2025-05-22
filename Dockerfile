# Используем официальный образ Python
FROM python:3.8-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

RUN pip install --upgrade pip

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для шаблонов заказов если ее нет
RUN mkdir -p /app/app/templates/orders

# Копируем шаблоны заказов
COPY app/templates/orders/new.html /app/app/templates/orders/
COPY app/templates/orders/index.html /app/app/templates/orders/
COPY app/templates/orders/view.html /app/app/templates/orders/
COPY app/templates/orders/edit.html /app/app/templates/orders/

# Делаем скрипт инициализации исполняемым
RUN chmod +x /app/app/init_data.py

# Создаем непривилегированного пользователя
RUN useradd -m myuser
RUN chown -R myuser:myuser /app
USER myuser

# Открываем порт
EXPOSE 5000

# Инициализируем базу данных и запускаем приложение
CMD python -c "from app.init_data import init_app; init_app()" && flask run --host=0.0.0.0 