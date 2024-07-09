FROM python:3.10-slim

WORKDIR /app

# Копирование зависимостей и их установка
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . /app

# Создание volume для базы данных
VOLUME ["/app/data"]

CMD ["python", "main.py"]