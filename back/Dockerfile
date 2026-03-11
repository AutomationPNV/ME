FROM python:3.11-slim

WORKDIR /app

# Системні пакети
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Копіюємо requirements спочатку (для кешування)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо ВМІСТ папки app у поточний WORKDIR (/app)
COPY ./app . 

# Встановлюємо змінну оточення прямо в образі
ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
