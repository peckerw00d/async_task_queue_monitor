FROM python:3.11-slim

WORKDIR /app

# Сначала скопируем всё — включая requirements.txt
COPY . .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
