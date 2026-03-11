from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database.connection import get_db_connection
from database.init_db import init_db

from api.add_motor import router as add_motor
from api.get_all_motors import router as get_all_motors
from api.delete_motor_by_id import router as delete_motor_by_id
from api.get_motor_by_ip import router as get_motor_by_ip
from api.update_motor import router as update_motor
import asyncio
import threading
import time
from fastapi import FastAPI
from services.test_modbus_service import (
    read_motor_data_modbus_mock, 
    insert_motor_data, 
    create_connection
)



app = FastAPI()

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # локальний фронт для dev
        "http://127.0.0.1:8080",  # локальний фронт
        "http://frontend:80",      # фронт у Docker
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Підключення до бази даних
get_db_connection()
    
# Ініціалізація таблиці при запуску
init_db()


# ==================== API ====================
# Отримати всі мотори
app.include_router(get_all_motors)

# Додати новий мотор
app.include_router(add_motor)

# Видалити мотор за ID
app.include_router(delete_motor_by_id)

# Отримати один мотор за ID
app.include_router(get_motor_by_ip)

# Оновити мотор
app.include_router(update_motor)




# ... ваші мідлвари та роутери ...

# ФУНКЦІЯ ДЛЯ ФОНОВОГО ЗБОРУ ДАНИХ
def run_data_collection():
    print("🚀 Starting data collection thread...")
    # Створюємо підключення спеціально для цього потоку
    connection = create_connection()
    
    motors = [
        {"name": "motor_01", "ip": "192.168.1.10"},
        {"name": "motor_02", "ip": "192.168.1.11"}
    ]

    try:
        while True:
            for motor in motors:
                data = read_motor_data_modbus_mock(motor["ip"])
                insert_motor_data(connection, motor["name"], motor["ip"], data)
            time.sleep(5)
    except Exception as e:
        print(f"❌ Error in collection loop: {e}")
    finally:
        if connection:
            connection.close()

# ЗАПУСК ПОТОКУ ПРИ СТАРТІ FASTAPI
@app.on_event("startup")
async def startup_event():
    # Запускаємо цикл у окремому потоці, щоб не блокувати FastAPI
    thread = threading.Thread(target=run_data_collection, daemon=True)
    thread.start()
