FROM python:3.12-slim

# Отключаем создание __pycache__ и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем системные зависимости GDAL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Настройка переменных окружения для GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install GDAL==$(gdal-config --version) && \
    pip install -r requirements.txt

# Копируем код и создаём папку для статики
COPY . /app/
RUN mkdir -p /app/staticfiles

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение (в production использовать gunicorn)
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Команда для миграций, сборки статики и запуска Gunicorn
CMD ["bash", "-c", "\
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn car_park.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers 3 \
      --timeout 120"]