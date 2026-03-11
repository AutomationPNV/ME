import random
import taosws  # ⬅️ Змінюємо на WebSocket для Docker
import time
from datetime import datetime
import os

# ----------------------------
# 1️⃣ Функція підключення
# ----------------------------
def create_connection():
    # В Docker використовуємо ім'я сервісу з docker-compose
    host = os.getenv("TDENGINE_HOST", "tdengine") 
    port = 6041  # ⬅️ Для WebSocket порт зазвичай 6041
    
    try:
        # Використовуємо taosws.connect
        conn = taosws.connect(
            user="root",
            password="taosdata",
            host=host,
            port=port,
            db="motor_db"  # В taosws параметр називається 'db'
        )
        print(f"✅ Connected to {host}:{port} via WebSocket successfully.")
        return conn
    except Exception as err:
        print(f"❌ Failed to connect to {host}:{port}, ErrMessage: {err}")
        # Робимо паузу і ретрай, бо база в Docker може запускатися довше за скрипт
        time.sleep(5)
        return create_connection()

# ----------------------------
# 2️⃣ Функція імітації Modbus (без змін)
# ----------------------------
def read_motor_data_modbus_mock(ip_tesys: str):
    return {
        "frequency": random.uniform(48.5, 51.5),
        "voltage_avg": random.uniform(210, 235),
        "voltage_unbalance": random.uniform(0, 2),
        "cos_phi": random.uniform(0.85, 0.98),
        "phase_unbalance": random.uniform(0, 1.5),
        "current_l1": random.uniform(5, 8),
        "current_l2": random.uniform(5, 8),
        "current_l3": random.uniform(5, 8),
        "vibration": random.uniform(0.01, 0.04)
    }

# ----------------------------
# 3️⃣ Функція вставки даних
# ----------------------------
def insert_motor_data(conn, motor_name, ip_tesys, data):
    cursor = conn.cursor()
    # TDengine любить формат таймстампу в мс або ISO рядком
    ts = datetime.now().isoformat()
    
    # Використовуємо синтаксис STABLE для автоматичного створення таблиць
    sql = f"""
    INSERT INTO {motor_name} USING motor_metrics TAGS ('{motor_name}', '{ip_tesys}')
    VALUES ('{ts}', {data["frequency"]}, {data["voltage_avg"]}, {data["voltage_unbalance"]}, 
            {data["cos_phi"]}, {data["phase_unbalance"]}, {data["current_l1"]}, 
            {data["current_l2"]}, {data["current_l3"]}, {data["vibration"]})
    """
    try:
        cursor.execute(sql)
        # В taosws commit() зазвичай не потрібен для вставки, але не завадить
        print(f"✅ Data inserted for motor {motor_name}")
    except Exception as e:
        print(f"❌ Failed to insert data: {e}")
    finally:
        cursor.close()

# ----------------------------
# 4️⃣ Основний цикл
# ----------------------------

    